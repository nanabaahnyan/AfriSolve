from rest_framework import generics, views, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import CustomUser
from .serializers import CustomUserSerializer, ChangePasswordSerializer
from problems.models import Problem, Application
from teams.models import Team
from problems.serializers import ApplicationSerializer
from .verification import verify_ghana_card_logic

class IsAdminRoleUser(permissions.BasePermission):
    """Allows access to users who are either Django staff or have the 'admin' role."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_staff))

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = CustomUserSerializer

    def create(self, request, *args, **kwargs):
        # 1. Identity Verification
        card_front = request.FILES.get('ghana_card_front')
        card_back = request.FILES.get('ghana_card_back')
        card_number = request.data.get('ghana_card_number')
        selfie = request.FILES.get('profile_image')

        if not all([card_front, card_back, card_number, selfie]):
            return Response({"error": "Missing required verification data."}, status=status.HTTP_400_BAD_REQUEST)

        # Performance note: This takes a few seconds
        verification = verify_ghana_card_logic(card_front, card_number, selfie)

        if not (verification["id_match"] and verification["face_match"]):
            return Response({
                "error": verification["error"] or "Identity verification failed."
            }, status=status.HTTP_400_BAD_REQUEST)

        # 2. Proceed with registration if verified
        return super().create(request, *args, **kwargs)

class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRoleUser]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRoleUser]

class DashboardStatsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRoleUser]

    def get(self, request):
        pending_apps = Application.objects.filter(status='pending').order_by('-created_at')
        stats = {
            'totalUsers': CustomUser.objects.count(),
            'activeProblems': Problem.objects.exclude(status='completed').count(),
            'completedProblems': Problem.objects.filter(status='completed').count(),
            'teamsCreated': Team.objects.count(),
            'pendingApprovalsCount': pending_apps.count(),
            'pendingApprovals': ApplicationSerializer(pending_apps, many=True).data,
        }
        return Response(stats)

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class ChangePasswordView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data.get("new_password"))
            user.save()
            return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeactivateAccountView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        user.is_active = False
        user.save()
        return Response({"message": "Account deactivated"}, status=status.HTTP_200_OK)


# ==========================================
# Native Django Template / SSR Frontend Views
# ==========================================

import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .forms import LoginForm, RegisterForm, ProfileForm, SettingsForm
from problems.models import Problem, Application
from teams.models import Team, TeamInvitation, TeamMembership

def home_view(request):
    return render(request, "home.html")

def faq_view(request):
    return render(request, "faq.html")

def terms_view(request):
    return render(request, "terms.html")

def privacy_view(request):
    return render(request, "privacy.html")

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
        
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = auth.authenticate(request, username=username, password=password)
            if user is not None:
                auth.login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
        
    return render(request, "login.html", {"form": form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
        
    default_role = request.GET.get("role", "poster")
    if default_role not in ["poster", "developer"]:
        default_role = "poster"

    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. Identity Verification
            card_front = request.FILES.get('ghana_card_front')
            card_back = request.FILES.get('ghana_card_back')
            card_number = form.cleaned_data.get('ghana_card_number')
            selfie = request.FILES.get('profile_image')

            # Performance note: This takes a few seconds
            verification = verify_ghana_card_logic(card_front, card_number, selfie)

            if not (verification["id_match"] and verification["face_match"]):
                err_msg = verification["error"] or "Identity verification failed."
                messages.error(request, err_msg)
                return render(request, "register.html", {"form": form, "default_role": default_role})

            # 2. Save User
            user = form.save(commit=False)
            
            # Generate username if not provided
            if not user.username:
                first = form.cleaned_data.get('first_name', '').lower()
                last = form.cleaned_data.get('last_name', '').lower()
                random_num = random.randint(1000, 9999)
                base_username = f"{first}_{last}" if first and last else "user"
                username = f"{base_username}_{random_num}"
                
                # Ensure uniqueness
                while CustomUser.objects.filter(username=username).exists():
                    random_num = random.randint(1000, 9999)
                    username = f"{base_username}_{random_num}"
                
                user.username = username

            # Set password securely
            user.set_password(form.cleaned_data["password"])
            user.is_staff = (user.role == "admin")
            user.save()
            
            auth.login(request, user)
            messages.success(request, f"Registration successful! Welcome to AfriSolve, {user.username}!")
            return redirect("dashboard")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = RegisterForm(initial={"role": default_role})
        
    return render(request, "register.html", {"form": form, "default_role": default_role})

def logout_view(request):
    auth.logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")

@login_required
def dashboard_view(request):
    user = request.user
    is_admin = user.role == "admin" or user.is_staff
    is_developer = user.role == "developer"

    if is_admin:
        # Load admin metrics
        pending_apps = Application.objects.filter(status='pending').order_by('-created_at')
        pending_teams = Team.objects.filter(status='pending_admin').order_by('-created_at')
        
        context = {
            "total_users": CustomUser.objects.count(),
            "active_problems": Problem.objects.exclude(status='completed').count(),
            "completed_problems": Problem.objects.filter(status='completed').count(),
            "teams_created": Team.objects.count(),
            "pending_approvals": pending_apps,
            "pending_teams": pending_teams,
            "is_admin": True
        }
    elif is_developer:
        # Developer views
        assigned_problems = Problem.objects.filter(assigned_developer=user).order_by('-created_at')
        teams = Team.objects.filter(memberships__developer=user).distinct().order_by('-created_at')
        invitations = TeamInvitation.objects.filter(invitee=user, status='pending').order_by('-invited_at')
        
        # Calculate stats for developer
        total = assigned_problems.count()
        completed = assigned_problems.filter(status='completed').count()
        in_progress = assigned_problems.filter(status__in=['assigned', 'in_progress']).count()
        avg_progress = 0
        if total > 0:
            avg_progress = round(sum(p.current_progress or 0 for p in assigned_problems) / total)
            
        completion_rate = round((completed / total) * 100) if total > 0 else 0
        performance_score = round((completion_rate * 0.6) + (avg_progress * 0.4))
        stars = max(1, min(5, round(performance_score / 20)))
        
        # Determine AI advice
        if total == 0:
            advice = {
                "title": "Get Started!",
                "text": "Browse open problems and apply to your first project. Completing your first project earns you your first star!",
                "icon": "🚀",
                "color": "from-blue-500 to-indigo-600"
            }
        elif performance_score >= 80:
            advice = {
                "title": "Outstanding Performer!",
                "text": f"You're in the top tier with a {performance_score}% performance score. Keep maintaining your delivery quality to unlock Elite status.",
                "icon": "🏆",
                "color": "from-amber-400 to-orange-500"
            }
        elif performance_score >= 60:
            advice = {
                "title": "Great Progress!",
                "text": f"Strong work with a {performance_score}% score. To climb further, aim to complete your active projects ahead of schedule.",
                "icon": "📈",
                "color": "from-green-500 to-emerald-600"
            }
        else:
            advice = {
                "title": "Keep Pushing!",
                "text": "Focus on completion — each finished project significantly boosts your score and visibility to new clients.",
                "icon": "💪",
                "color": "from-purple-500 to-indigo-600"
            }

        context = {
            "projects": assigned_problems,
            "teams": teams,
            "invitations": invitations,
            "total_projects": total,
            "completed_projects": completed,
            "in_progress_projects": in_progress,
            "avg_progress": avg_progress,
            "performance_score": performance_score,
            "stars": stars,
            "stars_range": range(1, 6),
            "advice": advice,
            "is_developer": True
        }
    else:
        # Poster views
        problems = Problem.objects.filter(poster=user).order_by('-created_at')
        completed = problems.filter(status='completed')
        in_development = problems.filter(status__in=['assigned', 'in_progress'])
        open_problems = problems.filter(status='open')
        
        context = {
            "total_posted": problems.count(),
            "completed_projects": completed,
            "in_development": in_development,
            "open_problems": open_problems,
            "is_poster": True
        }

    return render(request, "dashboard.html", context)

@login_required
def profile_view(request):
    user = request.user
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form = ProfileForm(instance=user)
    
    return render(request, "profile.html", {"form": form})

@login_required
def settings_view(request):
    user = request.user
    
    if request.method == "POST":
        action = request.POST.get("action")
        
        if action == "update_settings":
            form = SettingsForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, "Settings updated successfully!")
                return redirect("settings")
                
        elif action == "change_password":
            old_pass = request.POST.get("old_password")
            new_pass = request.POST.get("new_password")
            confirm_pass = request.POST.get("confirm_password")
            
            if not user.check_password(old_pass):
                messages.error(request, "Incorrect old password.")
            elif new_pass != confirm_pass:
                messages.error(request, "New passwords do not match.")
            else:
                user.set_password(new_pass)
                user.save()
                auth.update_session_auth_hash(request, user) # keep user logged in
                messages.success(request, "Password updated successfully!")
                return redirect("settings")
                
        elif action == "deactivate":
            user.is_active = False
            user.save()
            auth.logout(request)
            messages.info(request, "Your account has been deactivated.")
            return redirect("home")
    
    # Render page
    settings_form = SettingsForm(instance=user)
    return render(request, "settings.html", {"settings_form": settings_form})

@login_required
def user_detail_view(request, pk):
    target_user = get_object_or_404(CustomUser, pk=pk)
    
    # Calculate stats for profile page
    assigned_problems = Problem.objects.filter(assigned_developer=target_user)
    completed_count = assigned_problems.filter(status='completed').count()
    active_count = assigned_problems.exclude(status='completed').count()
    
    context = {
        "profile_user": target_user,
        "completed_count": completed_count,
        "active_count": active_count,
    }
    return render(request, "users/detail.html", context)
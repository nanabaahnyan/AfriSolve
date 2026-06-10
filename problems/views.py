from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Problem, Application, ProgressUpdate, Message, EscrowAgreement
from .serializers import ProblemSerializer, ApplicationSerializer, ProgressUpdateSerializer, MessageSerializer, EscrowAgreementSerializer


def get_problem_team(problem):
    """Return the active Team of the assigned developer, or None if solo/unassigned."""
    if not problem.assigned_developer:
        return None
    from teams.models import TeamMembership
    membership = TeamMembership.objects.filter(
        developer=problem.assigned_developer,
        team__status='active'
    ).select_related('team', 'team__leader').first()
    return membership.team if membership else None


def is_authorized_for_chat(problem, user):
    """Return True if user may read/write messages for this problem."""
    if user == problem.poster or user.is_staff:
        return True
    if user == problem.assigned_developer:
        return True
    # All members of the assigned team may chat
    team = get_problem_team(problem)
    if team:
        from teams.models import TeamMembership
        return TeamMembership.objects.filter(team=team, developer=user).exists()
    return False

class ProblemListCreateView(generics.ListCreateAPIView):
    queryset = Problem.objects.all().order_by('-created_at')
    serializer_class = ProblemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        try:
            if self.request.user.role != 'poster' and not self.request.user.is_staff:
                raise Exception("Only posters can create problems.")
            serializer.save(poster=self.request.user)
        except Exception as e:
            raise PermissionDenied(str(e))


class MyProblemsView(generics.ListAPIView):
    """Returns only the problems posted by the authenticated user."""
    serializer_class = ProblemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Problem.objects.filter(poster=self.request.user).order_by('-created_at')

class ProblemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        try:
            problem = self.get_object()
            if problem.poster != self.request.user and not self.request.user.is_staff:
                raise Exception("Unauthorized to update this problem.")
            serializer.save()
        except Exception as e:
            raise PermissionDenied(str(e))

class ApplicationCreateView(generics.CreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        try:
            if self.request.user.role != 'developer':
                raise Exception("Only developers can apply for problems.")
            serializer.save(developer=self.request.user)
        except Exception as e:
            raise PermissionDenied(str(e))

class ApplicationListView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Application.objects.all()
        if user.role == 'poster':
            return Application.objects.filter(problem__poster=user)
        return Application.objects.filter(developer=user)

class ProgressUpdateCreateView(generics.CreateAPIView):
    queryset = ProgressUpdate.objects.all()
    serializer_class = ProgressUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        try:
            problem = serializer.validated_data['problem']
            percentage = serializer.validated_data['percentage']
            if problem.assigned_developer != self.request.user and not self.request.user.is_staff:
                raise Exception("Only the assigned developer can update progress.")
            
            serializer.save(developer=self.request.user)
            
            # If progress percentage is 100%, trigger the escrow completion review clock
            if percentage == 100:
                escrow = problem.escrow_agreements.filter(status='fully_funded').first()
                if escrow:
                    from django.utils import timezone
                    escrow.completed_at = timezone.now()
                    escrow.save()
                    
                    # Create System Message in Chat
                    Message.objects.create(
                        problem=problem,
                        sender=self.request.user,
                        content="SYSTEM: Developer has marked the project as 100% Completed. The 7-day review period has started. Poster, please review the deliverables and Release Escrow or open a dispute."
                    )
        except Exception as e:
            raise PermissionDenied(str(e))

class ProgressUpdateListView(generics.ListAPIView):
    serializer_class = ProgressUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        problem_id = self.kwargs['problem_id']
        return ProgressUpdate.objects.filter(problem_id=problem_id).order_by('-created_at')

class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        problem_id = self.kwargs['problem_id']
        problem = Problem.objects.select_related('poster', 'assigned_developer').get(id=problem_id)
        user = self.request.user

        # Poster, assigned developer, all team members, and admins may read
        if is_authorized_for_chat(problem, user):
            return Message.objects.filter(problem_id=problem_id).order_by('created_at')

        raise PermissionDenied("You are not authorized to view messages for this project.")

    def perform_create(self, serializer):
        problem_id = self.kwargs['problem_id']
        problem = Problem.objects.select_related('poster', 'assigned_developer').get(id=problem_id)
        user = self.request.user

        if is_authorized_for_chat(problem, user):
            serializer.save(sender=user, problem=problem)
        else:
            raise PermissionDenied("You are not authorized to send messages for this project.")

class ApplicationResponseView(generics.UpdateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        application = self.get_object()
        problem = application.problem
        user = request.user
        
        # Only the problem poster or admin can approve/reject
        if problem.poster != user and not user.is_staff:
            return Response({"error": "Unauthorized to respond to this application"}, status=status.HTTP_403_FORBIDDEN)
            
        action = request.data.get('action') # 'approve' or 'reject'
        
        if action == 'approve':
            application.status = 'approved'
            application.save()
            
            # Update problem
            problem.status = 'assigned'
            problem.assigned_developer = application.developer
            problem.save()
            
            # Reject other applications for this problem
            Application.objects.filter(problem=problem).exclude(id=application.id).update(status='rejected')
            
            return Response({"message": "Application approved and developer assigned."})
            
        elif action == 'reject':
            application.status = 'rejected'
            application.save()
            return Response({"message": "Application rejected."})
            
        return Response({"error": "Invalid action. Use 'approve' or 'reject'"}, status=status.HTTP_400_BAD_REQUEST)


class EscrowProposeView(generics.CreateAPIView):
    serializer_class = EscrowAgreementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        problem_id = self.kwargs['problem_id']
        try:
            problem = Problem.objects.get(id=problem_id)
        except Problem.DoesNotExist:
            raise PermissionDenied("Project not found.")
            
        user = self.request.user
        
        # Access control: ONLY administrators / staff can propose the escrow agreement
        if not user.is_staff and user.role != 'admin':
            raise PermissionDenied("Only administrators can propose the escrow agreement.")
            
        # Check if active escrow already exists
        existing = EscrowAgreement.objects.filter(problem=problem).exclude(status='cancelled').first()
        if existing:
            raise PermissionDenied("An active escrow agreement already exists for this project.")
            
        agreed_cost = serializer.validated_data['agreed_cost']
        
        # Set status directly to 'agreed' since Admin sets this after mutual verbal agreement in chat
        escrow = serializer.save(
            problem=problem,
            proposed_by=user,
            status='agreed'
        )
        
        # Post a System Message in Chat
        Message.objects.create(
            problem=problem,
            sender=user,
            content=f"SYSTEM: Administrator {user.username} has established a Project Escrow Agreement with an agreed cost of {agreed_cost} GHS. Both parties can now deposit their 20% security deposit ({escrow.poster_deposit} GHS) to unlock the project."
        )


class EscrowAcceptView(generics.UpdateAPIView):
    queryset = EscrowAgreement.objects.all()
    serializer_class = EscrowAgreementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        escrow = self.get_object()
        user = request.user
        problem = escrow.problem
        
        # Must be the OTHER party in the project
        if user == escrow.proposed_by:
            return Response({"error": "You cannot accept your own proposed agreement."}, status=status.HTTP_400_BAD_REQUEST)
            
        if user != problem.poster and user != problem.assigned_developer and not user.is_staff:
            return Response({"error": "Unauthorized to accept this escrow."}, status=status.HTTP_403_FORBIDDEN)
            
        if escrow.status != 'proposed':
            return Response({"error": f"Escrow is in {escrow.status} state and cannot be accepted."}, status=status.HTTP_400_BAD_REQUEST)
            
        escrow.status = 'agreed'
        escrow.save()
        
        # Post System Message in Chat
        Message.objects.create(
            problem=problem,
            sender=user,
            content=f"SYSTEM: {user.username} accepted the Escrow Agreement! Both parties can now deposit their 20% security deposit ({escrow.poster_deposit} GHS) to unlock the work."
        )
        
        return Response(EscrowAgreementSerializer(escrow).data)


class EscrowVerifyPaymentView(generics.UpdateAPIView):
    queryset = EscrowAgreement.objects.all()
    serializer_class = EscrowAgreementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        escrow = self.get_object()
        user = request.user
        problem = escrow.problem
        reference = request.data.get('reference')

        if not reference:
            return Response({"error": "Paystack payment reference is required."}, status=status.HTTP_400_BAD_REQUEST)

        is_poster = (user == problem.poster)

        # Determine who is the authorised developer-side payer.
        # For a team project that is the Team Lead; for a solo project it is the assigned developer.
        team = get_problem_team(problem)
        if team:
            authorized_dev_payer = team.leader
        else:
            authorized_dev_payer = problem.assigned_developer

        is_authorized_dev_payer = (user == authorized_dev_payer)

        if not is_poster and not is_authorized_dev_payer and not user.is_staff:
            if team and user != problem.assigned_developer:
                # Give a clear message to regular team members
                from teams.models import TeamMembership
                if TeamMembership.objects.filter(team=team, developer=user).exists():
                    return Response(
                        {"error": f"Only the Team Lead ({team.leader.username}) can pay the developer security deposit."},
                        status=status.HTTP_403_FORBIDDEN
                    )
            return Response({"error": "Unauthorized to verify payments for this project."}, status=status.HTTP_403_FORBIDDEN)

        # Amount calculation
        expected_deposit = escrow.poster_deposit if is_poster else escrow.developer_deposit

        from .paystack import verify_paystack_payment
        verification = verify_paystack_payment(reference, expected_deposit)

        if not verification.get('status'):
            return Response({"error": verification.get('message', 'Paystack payment verification failed.')}, status=status.HTTP_400_BAD_REQUEST)

        # Update model based on roles
        if is_poster:
            if escrow.poster_paid:
                return Response({"message": "Poster deposit already verified.", "escrow": EscrowAgreementSerializer(escrow).data})
            escrow.poster_paid = True
            escrow.poster_tx_ref = reference
        elif is_authorized_dev_payer:
            if escrow.developer_paid:
                return Response({"message": "Developer deposit already verified.", "escrow": EscrowAgreementSerializer(escrow).data})
            escrow.developer_paid = True
            escrow.developer_tx_ref = reference
            
        # Adjust Status
        if escrow.poster_paid and escrow.developer_paid:
            escrow.status = 'fully_funded'
            # Update problem status to assigned, lock it
            problem.status = 'assigned'
            problem.save()
            system_msg = f"SYSTEM: Escrow is FULLY FUNDED (40% total deposit paid)! Work is officially unlocked and active."
        else:
            escrow.status = 'partially_funded'
            system_msg = f"SYSTEM: {user.username} has deposited their 20% security deposit ({expected_deposit} GHS)."
            
        escrow.save()
        
        # Post system chat message
        Message.objects.create(
            problem=problem,
            sender=user,
            content=system_msg
        )
        
        # Create a notification for the other user
        from notifications.models import Notification
        other_user = problem.assigned_developer if is_poster else problem.poster
        if other_user:
            Notification.objects.create(
                user=other_user,
                message=f"Escrow payment update for project '{problem.title}': {system_msg}"
            )
        
        return Response(EscrowAgreementSerializer(escrow).data)


class EscrowReleaseView(generics.UpdateAPIView):
    queryset = EscrowAgreement.objects.all()
    serializer_class = EscrowAgreementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        escrow = self.get_object()
        user = request.user
        problem = escrow.problem
        
        # Only the problem poster or admin can release the escrow
        if user != problem.poster and not user.is_staff:
            return Response({"error": "Only the project poster can release the escrow."}, status=status.HTTP_403_FORBIDDEN)
            
        if escrow.status != 'fully_funded':
            return Response({"error": "Only fully funded escrows can be released."}, status=status.HTTP_400_BAD_REQUEST)
            
        from django.utils import timezone
        escrow.status = 'completed'
        escrow.completed_at = timezone.now()
        escrow.save()
        
        # Update problem status
        problem.status = 'completed'
        problem.save()
        
        # Post system message
        Message.objects.create(
            problem=problem,
            sender=user,
            content=f"SYSTEM: {user.username} approved the deliverables and released the Escrow! The 40% security deposit is dispatched to the developer. Poster, please pay the remaining 80% balance ({float(escrow.agreed_cost) * 0.8} GHS) to finish the contract."
        )
        
        # Notify developer
        from notifications.models import Notification
        if problem.assigned_developer:
            Notification.objects.create(
                user=problem.assigned_developer,
                message=f"Congratulations! The poster has approved project '{problem.title}' and released your escrow and payout."
            )
        
        return Response(EscrowAgreementSerializer(escrow).data)


class EscrowDisputeView(generics.UpdateAPIView):
    queryset = EscrowAgreement.objects.all()
    serializer_class = EscrowAgreementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        escrow = self.get_object()
        user = request.user
        problem = escrow.problem
        
        # Either developer or poster can dispute
        if user != problem.poster and user != problem.assigned_developer and not user.is_staff:
            return Response({"error": "Unauthorized to dispute this project."}, status=status.HTTP_403_FORBIDDEN)
            
        if escrow.status not in ['fully_funded', 'partially_funded']:
            return Response({"error": "Cannot dispute an inactive or completed escrow."}, status=status.HTTP_400_BAD_REQUEST)
            
        escrow.status = 'disputed'
        escrow.save()
        
        # Post system message
        Message.objects.create(
            problem=problem,
            sender=user,
            content=f"SYSTEM: A dispute has been filed by {user.username} regarding this project. Escrow funds are frozen. An AfriSolve administrator will investigate and contact both parties."
        )
        
        return Response(EscrowAgreementSerializer(escrow).data)


class EscrowActiveView(generics.GenericAPIView):
    serializer_class = EscrowAgreementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, problem_id):
        try:
            problem = Problem.objects.select_related('poster', 'assigned_developer').get(id=problem_id)
        except Problem.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if not is_authorized_for_chat(problem, user):
            return Response({"error": "Unauthorized to view escrow details."}, status=status.HTTP_403_FORBIDDEN)

        escrow = EscrowAgreement.objects.filter(problem=problem).exclude(status='cancelled').first()
        if not escrow:
            return Response(None, status=status.HTTP_200_OK)

        return Response(EscrowAgreementSerializer(escrow).data)


class EscrowTeamInfoView(generics.GenericAPIView):
    """Returns team context for the assigned developer side of a project.
    Used by the frontend to decide who shows the payment button and who can chat."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, problem_id):
        try:
            problem = Problem.objects.select_related('poster', 'assigned_developer').get(id=problem_id)
        except Problem.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        # Allow anyone who can chat to fetch team info
        if not is_authorized_for_chat(problem, user) and user != problem.poster and not user.is_staff:
            return Response({"error": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)

        if not problem.assigned_developer:
            return Response({
                "is_team_project": False,
                "team_name": None,
                "team_lead_id": None,
                "team_lead_username": None,
                "current_user_is_team_lead": False,
                "current_user_is_team_member": False,
            })

        team = get_problem_team(problem)

        if not team:
            # Solo developer
            return Response({
                "is_team_project": False,
                "team_name": None,
                "team_lead_id": problem.assigned_developer.id,
                "team_lead_username": problem.assigned_developer.username,
                "current_user_is_team_lead": user == problem.assigned_developer,
                "current_user_is_team_member": user == problem.assigned_developer,
            })

        from teams.models import TeamMembership
        user_in_team = TeamMembership.objects.filter(team=team, developer=user).exists()
        user_is_lead = (team.leader == user)

        return Response({
            "is_team_project": True,
            "team_name": team.name,
            "team_lead_id": team.leader.id,
            "team_lead_username": team.leader.username,
            "current_user_is_team_lead": user_is_lead,
            "current_user_is_team_member": user_in_team,
        })


# ──────────────────────────────────────────────
# Template (SSR) Views
# ──────────────────────────────────────────────
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages as django_messages


def problem_list_view(request):
    category = request.GET.get('category', '')
    problems = Problem.objects.all().order_by('-created_at')
    if category and category != 'All Categories':
        problems = problems.filter(category=category)
    return render(request, 'problems/list.html', {
        'problems': problems,
        'selected_category': category,
        'categories': ['Health & Environment', 'Commerce', 'Education & Transport', 'Agriculture', 'Other'],
    })


def problem_detail_view(request, pk):
    problem = get_object_or_404(Problem, pk=pk)
    user = request.user

    is_authorized_chat = False
    if user.is_authenticated:
        is_authorized_chat = is_authorized_for_chat(problem, user)

    # Handle apply form POST
    if request.method == 'POST' and user.is_authenticated:
        estimated_duration = request.POST.get('estimated_duration', '')
        message = request.POST.get('message', '')
        if estimated_duration:
            Application.objects.create(
                problem=problem,
                developer=user,
                estimated_duration=estimated_duration,
                message=message,
            )
            django_messages.success(request, 'Application submitted successfully!')
            return redirect('problems:detail', pk=pk)

    user_has_applied = False
    if user.is_authenticated:
        user_has_applied = Application.objects.filter(problem=problem, developer=user).exists()

    return render(request, 'problems/detail.html', {
        'problem': problem,
        'is_authorized_chat': is_authorized_chat,
        'user_has_applied': user_has_applied,
    })


@login_required
def problem_chat_view(request, pk):
    problem = get_object_or_404(Problem, pk=pk)
    user = request.user

    if not is_authorized_for_chat(problem, user):
        return render(request, 'problems/chat_denied.html', {'problem': problem})

    is_poster = (user == problem.poster)

    # Get team info
    team = get_problem_team(problem)
    team_info = None
    if team:
        from teams.models import TeamMembership
        team_info = {
            'is_team_project': True,
            'team_name': team.name,
            'team_lead_id': team.leader.id,
            'team_lead_username': team.leader.username,
            'current_user_is_team_lead': team.leader == user,
            'current_user_is_team_member': TeamMembership.objects.filter(team=team, developer=user).exists(),
        }
    elif problem.assigned_developer:
        team_info = {
            'is_team_project': False,
            'team_lead_id': problem.assigned_developer.id,
            'team_lead_username': problem.assigned_developer.username,
            'current_user_is_team_lead': user == problem.assigned_developer,
            'current_user_is_team_member': user == problem.assigned_developer,
        }

    # Get messages
    chat_messages = Message.objects.filter(problem=problem).order_by('created_at').select_related('sender')

    # Get active escrow
    escrow = EscrowAgreement.objects.filter(problem=problem).exclude(status='cancelled').first()

    can_pay_dev_deposit = False
    if team_info:
        can_pay_dev_deposit = team_info.get('current_user_is_team_lead', False)
    elif problem.assigned_developer:
        can_pay_dev_deposit = (user == problem.assigned_developer)

    return render(request, 'problems/chat.html', {
        'problem': problem,
        'chat_messages': chat_messages,
        'escrow': escrow,
        'is_poster': is_poster,
        'team_info': team_info,
        'can_pay_dev_deposit': can_pay_dev_deposit,
        'is_admin': user.is_staff or getattr(user, 'role', '') == 'admin',
    })


@login_required
def problem_post_view(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', '').strip()
        location = request.POST.get('location', '').strip()
        description = request.POST.get('description', '').strip()
        business_impact = request.POST.get('business_impact', '').strip()

        if not (title and category and description):
            django_messages.error(request, 'Title, category, and description are required.')
        elif request.user.role != 'poster' and not request.user.is_staff:
            django_messages.error(request, 'Only Posters can submit problems.')
        else:
            Problem.objects.create(
                title=title,
                category=category,
                location=location,
                description=description,
                business_impact=business_impact,
                poster=request.user,
            )
            django_messages.success(request, 'Problem posted successfully!')
            return redirect('dashboard')

    return render(request, 'problems/post.html', {
        'categories': ['Health & Environment', 'Commerce', 'Education & Transport', 'Agriculture', 'Other'],
    })


@login_required
@require_POST
def progress_create_view(request, pk=None):
    """AJAX-friendly progress update endpoint called from dashboard or chat."""
    from django.http import JsonResponse
    problem_id = request.POST.get('problem')
    percentage = request.POST.get('percentage')

    try:
        problem = Problem.objects.get(id=problem_id)
        if problem.assigned_developer != request.user and not request.user.is_staff:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        update = ProgressUpdate.objects.create(
            problem=problem,
            developer=request.user,
            percentage=int(percentage),
        )
        if int(percentage) == 100:
            escrow = problem.escrow_agreements.filter(status='fully_funded').first()
            if escrow:
                from django.utils import timezone
                escrow.completed_at = timezone.now()
                escrow.save()
                Message.objects.create(
                    problem=problem,
                    sender=request.user,
                    content="SYSTEM: Developer has marked the project as 100% Completed. The 7-day review period has started. Poster, please review the deliverables and Release Escrow or open a dispute."
                )
        return JsonResponse({'success': True, 'percentage': update.percentage})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

from django.utils import timezone
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Team, TeamMembership, TeamInvitation
from .serializers import TeamSerializer, TeamMembershipSerializer, TeamInvitationSerializer
from users.models import CustomUser
from notifications.models import Notification


def user_in_active_team(user):
    """Return True if the user already belongs to an active team."""
    return TeamMembership.objects.filter(
        developer=user,
        team__status='active'
    ).exists()


class TeamListCreateView(generics.ListCreateAPIView):
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            return Team.objects.all().order_by('-created_at')
        # Developers see teams they lead or are members of
        return Team.objects.filter(
            memberships__developer=user
        ).distinct().order_by('-created_at')

    def create(self, request, *args, **kwargs):
        user = request.user

        if user.role != 'developer' and not user.is_staff:
            return Response({"error": "Only developers can create teams."}, status=400)

        if user_in_active_team(user):
            return Response({"error": "You are already in an active team. A developer can only belong to one team."}, status=400)

        # Check if user already has a pending/draft team they lead
        existing = Team.objects.filter(leader=user, status__in=['draft', 'pending_admin']).first()
        if existing:
            return Response({"error": f"You already have a pending team '{existing.name}'. Wait for it to be resolved before creating another."}, status=400)

        member_usernames = request.data.get('member_usernames', [])

        # Validate members
        members = []
        for username in member_usernames:
            if username == user.username:
                continue  # skip self
            try:
                member = CustomUser.objects.get(username=username, role='developer')
            except CustomUser.DoesNotExist:
                return Response({"error": f"Developer '{username}' not found. Only developers can join teams."}, status=400)

            if user_in_active_team(member):
                return Response({"error": f"'{username}' is already in an active team and cannot join another."}, status=400)

            # Check if they already have a pending invite for another team
            pending_invite = TeamInvitation.objects.filter(invitee=member, status='pending').first()
            if pending_invite:
                return Response({"error": f"'{username}' already has a pending invitation for team '{pending_invite.team.name}'."}, status=400)

            members.append(member)

        # Create the team
        team = Team.objects.create(
            name=request.data.get('name'),
            description=request.data.get('description', ''),
            leader=user,
            status='draft'
        )

        # Create invitations for each proposed member
        for member in members:
            TeamInvitation.objects.create(team=team, invitee=member)
            Notification.objects.create(
                user=member,
                message=f"🤝 {user.username} has invited you to join the team '{team.name}'. Go to your dashboard to accept or decline."
            )

        # If no members invited, team goes straight to pending_admin
        if not members:
            team.status = 'pending_admin'
            team.save()
            # Create leader membership
            TeamMembership.objects.create(team=team, developer=user, role='Team Lead')
            # Notify admin
            for admin in CustomUser.objects.filter(role='admin'):
                Notification.objects.create(
                    user=admin,
                    message=f"📋 A new solo team '{team.name}' by {user.username} is awaiting your approval."
                )

        serializer = TeamSerializer(team)
        return Response(serializer.data, status=201)


class TeamDetailView(generics.RetrieveUpdateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        team = self.get_object()
        if team.leader != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Only the team leader can update team info.")
        serializer.save()


class TeamInvitationResponseView(views.APIView):
    """Developer accepts or declines a team invitation."""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            invitation = TeamInvitation.objects.get(pk=pk, invitee=request.user)
        except TeamInvitation.DoesNotExist:
            return Response({"error": "Invitation not found."}, status=404)

        if invitation.status != 'pending':
            return Response({"error": "This invitation has already been responded to."}, status=400)

        action = request.data.get('action')  # 'accept' or 'decline'

        if action == 'accept':
            # Last-minute check: ensure not already in active team
            if user_in_active_team(request.user):
                return Response({"error": "You are already in an active team."}, status=400)

            invitation.status = 'accepted'
            invitation.responded_at = timezone.now()
            invitation.save()

            # Notify team leader
            Notification.objects.create(
                user=invitation.team.leader,
                message=f"✅ {request.user.username} accepted your invitation to join '{invitation.team.name}'."
            )

            # Check if all invitations are now accepted
            team = invitation.team
            if team.all_invitations_accepted():
                team.status = 'pending_admin'
                team.save()

                # Create leader membership now (members created on admin approval)
                TeamMembership.objects.get_or_create(
                    team=team,
                    developer=team.leader,
                    defaults={'role': 'Team Lead'}
                )

                # Notify admin
                for admin in CustomUser.objects.filter(role='admin'):
                    Notification.objects.create(
                        user=admin,
                        message=f"📋 Team '{team.name}' has all members confirmed and is awaiting your approval."
                    )

                # Notify leader
                Notification.objects.create(
                    user=team.leader,
                    message=f"🎉 All members accepted! Team '{team.name}' is now pending admin approval."
                )

        elif action == 'decline':
            invitation.status = 'declined'
            invitation.responded_at = timezone.now()
            invitation.save()

            # Notify team leader
            Notification.objects.create(
                user=invitation.team.leader,
                message=f"❌ {request.user.username} declined your invitation to join '{invitation.team.name}'."
            )

        else:
            return Response({"error": "Invalid action. Use 'accept' or 'decline'."}, status=400)

        return Response(TeamInvitationSerializer(invitation).data)


class TeamAdminApprovalView(views.APIView):
    """Admin approves or rejects a pending team."""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        if not request.user.is_staff and request.user.role != 'admin':
            return Response({"error": "Admin access required."}, status=403)

        try:
            team = Team.objects.get(pk=pk, status='pending_admin')
        except Team.DoesNotExist:
            return Response({"error": "Team not found or not pending approval."}, status=404)

        action = request.data.get('action')  # 'approve' or 'reject'

        if action == 'approve':
            # Final one-team check for all accepted members
            for invite in team.invitations.filter(status='accepted'):
                if user_in_active_team(invite.invitee):
                    return Response({
                        "error": f"Cannot approve: '{invite.invitee.username}' joined another team since being invited."
                    }, status=400)

            team.status = 'active'
            team.save()

            # Create memberships for all accepted invitees
            for invite in team.invitations.filter(status='accepted'):
                TeamMembership.objects.get_or_create(
                    team=team,
                    developer=invite.invitee,
                    defaults={'role': 'Member'}
                )

            # Ensure leader membership exists with Team Lead role
            TeamMembership.objects.update_or_create(
                team=team,
                developer=team.leader,
                defaults={'role': 'Team Lead'}
            )

            # Notify all members
            all_members = [team.leader] + [i.invitee for i in team.invitations.filter(status='accepted')]
            for member in all_members:
                role_label = 'Team Lead' if member == team.leader else 'Member'
                Notification.objects.create(
                    user=member,
                    message=f"🏆 Your team '{team.name}' has been approved by the admin! Your role: {role_label}."
                )

        elif action == 'reject':
            team.status = 'rejected'
            team.save()

            # Notify leader
            Notification.objects.create(
                user=team.leader,
                message=f"❌ Your team '{team.name}' was rejected by the admin."
            )

        else:
            return Response({"error": "Invalid action. Use 'approve' or 'reject'."}, status=400)

        return Response(TeamSerializer(team).data)


class MyInvitationsView(generics.ListAPIView):
    """List all pending invitations for the logged-in developer."""
    serializer_class = TeamInvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TeamInvitation.objects.filter(
            invitee=self.request.user,
            status='pending'
        ).order_by('-invited_at')


class PendingTeamsView(generics.ListAPIView):
    """Admin view: list all teams pending approval."""
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]


    def get_queryset(self):
        if not self.request.user.is_staff and self.request.user.role != 'admin':
            return Team.objects.none()
        return Team.objects.filter(status='pending_admin').order_by('-created_at')


# ──────────────────────────────────────────────
# Template (SSR) Views
# ──────────────────────────────────────────────
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import TeamForm


@login_required
def team_create_view(request):
    user = request.user
    if user.role != 'developer' and not user.is_staff:
        messages.error(request, "Only developers can create teams.")
        return redirect("dashboard")

    if user_in_active_team(user):
        messages.error(request, "You are already in an active team.")
        return redirect("dashboard")

    # Check if user already has a pending/draft team they lead
    existing = Team.objects.filter(leader=user, status__in=['draft', 'pending_admin']).first()
    if existing:
        messages.error(request, f"You already have a pending team '{existing.name}'. Wait for it to be resolved before creating another.")
        return redirect("dashboard")

    if request.method == "POST":
        form = TeamForm(request.POST)
        if form.is_valid():
            # Process member usernames
            raw_usernames = form.cleaned_data.get("member_usernames", "")
            member_usernames = [u.strip() for u in raw_usernames.split(",") if u.strip()]
            
            # Remove self
            member_usernames = [u for u in member_usernames if u != user.username]
            
            # Validate members
            members = []
            has_error = False
            for username in member_usernames:
                try:
                    member = CustomUser.objects.get(username=username, role='developer')
                except CustomUser.DoesNotExist:
                    messages.error(request, f"Developer '{username}' not found. Only registered developers can join teams.")
                    has_error = True
                    break

                if user_in_active_team(member):
                    messages.error(request, f"'{username}' is already in an active team.")
                    has_error = True
                    break

                pending_invite = TeamInvitation.objects.filter(invitee=member, status='pending').first()
                if pending_invite:
                    messages.error(request, f"'{username}' already has a pending invitation for team '{pending_invite.team.name}'.")
                    has_error = True
                    break

                members.append(member)

            if not has_error:
                # Create the team
                team = form.save(commit=False)
                team.leader = user
                team.status = 'draft'
                team.save()

                # Create invitations
                for member in members:
                    TeamInvitation.objects.create(team=team, invitee=member)
                    Notification.objects.create(
                        user=member,
                        message=f"🤝 {user.username} has invited you to join the team '{team.name}'. Go to your dashboard to accept or decline."
                    )

                if not members:
                    team.status = 'pending_admin'
                    team.save()
                    TeamMembership.objects.create(team=team, developer=user, role='Team Lead')
                    
                    # Notify admin
                    for admin in CustomUser.objects.filter(role='admin'):
                        Notification.objects.create(
                            user=admin,
                            message=f"📋 A new solo team '{team.name}' by {user.username} is awaiting approval."
                        )
                    messages.success(request, f"Team '{team.name}' created and sent to admin for approval.")
                else:
                    messages.success(request, f"Team '{team.name}' created and invitations sent to proposed members.")
                
                return redirect("dashboard")
    else:
        form = TeamForm()

    return render(request, "teams/create.html", {"form": form})


@login_required
def team_detail_view(request, pk):
    team = get_object_or_404(Team, pk=pk)
    memberships = team.memberships.select_related('developer').all()
    user_is_member = memberships.filter(developer=request.user).exists()
    user_is_leader = (team.leader == request.user)

    if not (user_is_member or user_is_leader or request.user.is_staff or getattr(request.user, 'role', '') == 'admin'):
        return render(request, 'teams/detail.html', {'team': None, 'access_denied': True})

    return render(request, 'teams/detail.html', {
        'team': team,
        'memberships': memberships,
        'user_is_leader': user_is_leader,
        'access_denied': False,
    })

from django.urls import path
from .views import (
    TeamListCreateView,
    TeamDetailView,
    TeamInvitationResponseView,
    TeamAdminApprovalView,
    MyInvitationsView,
    PendingTeamsView,
)

urlpatterns = [
    path('', TeamListCreateView.as_view(), name='team_list_create'),
    path('<int:pk>/', TeamDetailView.as_view(), name='team_detail'),
    path('<int:pk>/approve/', TeamAdminApprovalView.as_view(), name='team_approve'),
    path('invitations/mine/', MyInvitationsView.as_view(), name='my_invitations'),
    path('invitations/<int:pk>/respond/', TeamInvitationResponseView.as_view(), name='invitation_respond'),
    path('pending/', PendingTeamsView.as_view(), name='pending_teams'),
]

from django.urls import path
from .views import (
    ProblemListCreateView, ProblemDetailView,
    ApplicationCreateView, ApplicationListView, ApplicationResponseView,
    ProgressUpdateCreateView, ProgressUpdateListView,
    MyProblemsView, MessageListCreateView,
    EscrowActiveView, EscrowProposeView, EscrowAcceptView,
    EscrowVerifyPaymentView, EscrowReleaseView, EscrowDisputeView,
    EscrowTeamInfoView,
)

urlpatterns = [
    # Problems & Boards
    path('', ProblemListCreateView.as_view(), name='problem_list_create'),
    path('mine/', MyProblemsView.as_view(), name='my_problems'),
    path('<int:pk>/', ProblemDetailView.as_view(), name='problem_detail'),
    
    # Applications / Proposals
    path('applications/', ApplicationListView.as_view(), name='application_list'),
    path('applications/create/', ApplicationCreateView.as_view(), name='application_create'),
    path('applications/<int:pk>/respond/', ApplicationResponseView.as_view(), name='application_respond'),
    
    # Progress Tracking & Chat
    path('<int:problem_id>/progress/', ProgressUpdateListView.as_view(), name='progress_list'),
    path('progress/create/', ProgressUpdateCreateView.as_view(), name='progress_create'),
    path('<int:problem_id>/messages/', MessageListCreateView.as_view(), name='message_list_create'),
    
    # Paystack Escrow Integration
    path('<int:problem_id>/escrow/active/', EscrowActiveView.as_view(), name='escrow_active'),
    path('<int:problem_id>/escrow/team-info/', EscrowTeamInfoView.as_view(), name='escrow_team_info'),
    path('<int:problem_id>/escrow/propose/', EscrowProposeView.as_view(), name='escrow_propose'),
    path('escrow/<int:pk>/accept/', EscrowAcceptView.as_view(), name='escrow_accept'),
    path('escrow/<int:pk>/verify/', EscrowVerifyPaymentView.as_view(), name='escrow_verify'),
    path('escrow/<int:pk>/release/', EscrowReleaseView.as_view(), name='escrow_release'),
    path('escrow/<int:pk>/dispute/', EscrowDisputeView.as_view(), name='escrow_dispute'),
]

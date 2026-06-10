from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, CustomTokenObtainPairView, DashboardStatsView, UserListView, UserDetailView, ProfileUpdateView, ChangePasswordView, DeactivateAccountView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('all/', UserListView.as_view(), name='user_list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('deactivate/', DeactivateAccountView.as_view(), name='deactivate_account'),
]
from django.urls import path
from .views import team_detail_view, team_create_view

app_name = 'teams'

urlpatterns = [
    path('create/', team_create_view, name='create'),
    path('<int:pk>/', team_detail_view, name='detail'),
]

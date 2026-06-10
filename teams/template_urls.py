from django.urls import path
from .views import team_detail_view

app_name = 'teams'

urlpatterns = [
    path('<int:pk>/', team_detail_view, name='detail'),
]

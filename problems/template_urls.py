from django.urls import path
from .views import (
    problem_list_view, problem_detail_view, 
    problem_chat_view, problem_post_view,
    progress_create_view
)

app_name = 'problems'

urlpatterns = [
    path('', problem_list_view, name='list'),
    path('<int:pk>/', problem_detail_view, name='detail'),
    path('<int:pk>/chat/', problem_chat_view, name='chat'),
    path('post/', problem_post_view, name='post'),
    path('progress/create/', progress_create_view, name='progress_create'),
]

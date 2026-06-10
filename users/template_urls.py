from django.urls import path
from .views import user_detail_view

urlpatterns = [
    path('<int:pk>/', user_detail_view, name='user_detail'),
]

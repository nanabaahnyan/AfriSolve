from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Notification
from .serializers import NotificationSerializer

class NotificationListCreateView(generics.ListCreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Notification.objects.all().order_by('-created_at')
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admins can manually create notifications.")
        serializer.save()

class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Notification.objects.all()
        return Notification.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admins can delete notifications.")
        instance.delete()

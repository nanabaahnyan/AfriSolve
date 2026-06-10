from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('poster', 'Problem Poster'),
        ('developer', 'Developer'),
        ('admin', 'Administrator'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='poster')
    ghana_card_number = models.CharField(max_length=20, blank=True, null=True)
    ghana_card_front = models.ImageField(upload_to='id_pictures/front/', blank=True, null=True)
    ghana_card_back = models.ImageField(upload_to='id_pictures/back/', blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    
    # User Preferences
    email_notifications = models.BooleanField(default=True)
    browser_notifications = models.BooleanField(default=True)
    marketing_notifications = models.BooleanField(default=False)
    update_notifications = models.BooleanField(default=True)
    
    public_profile = models.BooleanField(default=True)
    show_email = models.BooleanField(default=False)
    
    # Social Links
    github_url = models.URLField(max_length=255, blank=True, null=True)
    linkedin_url = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

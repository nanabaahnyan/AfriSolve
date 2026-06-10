from rest_framework import serializers
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

import random

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'role', 'password', 'date_joined', 'ghana_card_number', 'ghana_card_front', 'ghana_card_back', 'profile_image', 'first_name', 'last_name', 
                  'email_notifications', 'browser_notifications', 'marketing_notifications', 'update_notifications', 'public_profile', 'show_email',
                  'github_url', 'linkedin_url')
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'username': {'required': False}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        role = validated_data.get('role', 'poster')
        is_staff = role == 'admin'
        
        # Generate username if not provided
        if not validated_data.get('username'):
            first = validated_data.get('first_name', '').lower()
            last = validated_data.get('last_name', '').lower()
            random_num = random.randint(1000, 9999)
            base_username = f"{first}_{last}" if first and last else "user"
            username = f"{base_username}_{random_num}"
            
            # Ensure uniqueness
            while CustomUser.objects.filter(username=username).exists():
                random_num = random.randint(1000, 9999)
                username = f"{base_username}_{random_num}"
            
            validated_data['username'] = username

        user = CustomUser.objects.create_user(
            password=password,
            is_staff=is_staff,
            **validated_data
        )
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        role = validated_data.get('role')
        if role:
            instance.is_staff = (role == 'admin')
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,
            'is_staff': self.user.is_staff,
            'profile_image': self.user.profile_image.url if self.user.profile_image else None,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email_notifications': self.user.email_notifications,
            'browser_notifications': self.user.browser_notifications,
            'marketing_notifications': self.user.marketing_notifications,
            'update_notifications': self.user.update_notifications,
            'public_profile': self.user.public_profile,
            'show_email': self.user.show_email,
            'github_url': self.user.github_url,
            'linkedin_url': self.user.linkedin_url,
        }
        return data

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value

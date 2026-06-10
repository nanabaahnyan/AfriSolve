from django import forms
from .models import CustomUser

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'})
    )

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
        label="Confirm Password"
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'first_name', 'last_name', 'email', 'role', 
            'ghana_card_number', 'ghana_card_front', 'ghana_card_back', 'profile_image'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Create username (Optional)'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'ghana_card_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. GHA-123456789-0'}),
            'ghana_card_front': forms.FileInput(attrs={'class': 'form-control'}),
            'ghana_card_back': forms.FileInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = False
        self.fields['ghana_card_front'].required = True
        self.fields['ghana_card_back'].required = True
        self.fields['profile_image'].required = True

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'profile_image', 
            'github_url', 'linkedin_url'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/username'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/username'}),
        }

class SettingsForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'email_notifications', 'browser_notifications', 
            'marketing_notifications', 'update_notifications',
            'public_profile', 'show_email'
        ]
        widgets = {
            'email_notifications': forms.CheckboxInput(),
            'browser_notifications': forms.CheckboxInput(),
            'marketing_notifications': forms.CheckboxInput(),
            'update_notifications': forms.CheckboxInput(),
            'public_profile': forms.CheckboxInput(),
            'show_email': forms.CheckboxInput(),
        }

from django import forms
from .models import Team

class TeamForm(forms.ModelForm):
    member_usernames = forms.CharField(
        required=False,
        label="Invite Members by Username",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter comma-separated usernames (e.g. kojo_dev, yaw_coder)'
        }),
        help_text="Invited developers will receive dashboard notifications to accept or decline before the team goes to admin review."
    )

    class Meta:
        model = Team
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a unique team name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about your team...'}),
        }

from django import forms
from .models import Problem, Application, ProgressUpdate

class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ['title', 'description', 'category', 'budget']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter clear title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe the problem in detail...', 'rows': 5}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Design, Web, Mobile'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 5000'}),
        }

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['estimated_duration', 'message']
        widgets = {
            'estimated_duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2 weeks'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your proposal approach details...', 'rows': 4}),
        }

class ProgressUpdateForm(forms.ModelForm):
    class Meta:
        model = ProgressUpdate
        fields = ['problem', 'percentage', 'note']
        widgets = {
            'problem': forms.HiddenInput(),
            'percentage': forms.Select(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

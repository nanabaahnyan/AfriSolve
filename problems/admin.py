from django.contrib import admin
from .models import Problem, Application, ProgressUpdate, Message, EscrowAgreement

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'status', 'poster', 'assigned_developer', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description', 'poster__username', 'assigned_developer__username')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'problem', 'developer', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('problem__title', 'developer__username')

@admin.register(ProgressUpdate)
class ProgressUpdateAdmin(admin.ModelAdmin):
    list_display = ('id', 'problem', 'developer', 'percentage', 'created_at')
    list_filter = ('percentage',)
    search_fields = ('problem__title', 'developer__username')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'problem', 'sender', 'content_snippet', 'created_at')
    search_fields = ('content', 'problem__title', 'sender__username')

    def content_snippet(self, obj):
        return obj.content[:50]
    content_snippet.short_description = 'Content'

@admin.register(EscrowAgreement)
class EscrowAgreementAdmin(admin.ModelAdmin):
    list_display = ('id', 'problem', 'agreed_cost', 'poster_deposit', 'developer_deposit', 'status', 'poster_paid', 'developer_paid', 'created_at')
    list_filter = ('status', 'poster_paid', 'developer_paid')
    search_fields = ('problem__title', 'proposed_by__username')

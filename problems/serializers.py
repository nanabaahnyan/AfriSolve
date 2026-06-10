from rest_framework import serializers
from .models import Problem, Application, ProgressUpdate, Message, EscrowAgreement
from users.serializers import CustomUserSerializer


class ProgressUpdateSerializer(serializers.ModelSerializer):
    developer_details = CustomUserSerializer(source='developer', read_only=True)

    class Meta:
        model = ProgressUpdate
        fields = '__all__'
        read_only_fields = ('developer',)


class ProblemSerializer(serializers.ModelSerializer):
    poster_details = CustomUserSerializer(source='poster', read_only=True)
    assigned_developer_details = CustomUserSerializer(source='assigned_developer', read_only=True)
    current_progress = serializers.SerializerMethodField()
    assigned_team_name = serializers.SerializerMethodField()

    class Meta:
        model = Problem
        fields = '__all__'
        read_only_fields = ('poster', 'assigned_developer', 'status')

    def get_current_progress(self, obj):
        latest = obj.progress_updates.order_by('-created_at').first()
        return latest.percentage if latest else 0

    def get_assigned_team_name(self, obj):
        """Return the name of the team the assigned developer belongs to (if any)."""
        if not obj.assigned_developer:
            return None
        from teams.models import TeamMembership
        membership = TeamMembership.objects.filter(
            developer=obj.assigned_developer,
            team__status='active'
        ).select_related('team').first()
        return membership.team.name if membership else None


class ApplicationSerializer(serializers.ModelSerializer):
    developer_details = CustomUserSerializer(source='developer', read_only=True)
    problem_details = ProblemSerializer(source='problem', read_only=True)

    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ('developer', 'status')


class MessageSerializer(serializers.ModelSerializer):
    sender_details = CustomUserSerializer(source='sender', read_only=True)
    reply_to_details = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ('id', 'problem', 'sender', 'sender_details', 'content', 'created_at', 'is_read', 'reply_to', 'reply_to_details')
        read_only_fields = ('sender', 'sender_details', 'created_at', 'is_read', 'problem', 'reply_to_details')

    def get_reply_to_details(self, obj):
        if obj.reply_to:
            return {
                'id': obj.reply_to.id,
                'content': obj.reply_to.content[:100],  # Short snippet
                'sender_username': obj.reply_to.sender.username
            }
        return None


class EscrowAgreementSerializer(serializers.ModelSerializer):
    proposed_by_details = CustomUserSerializer(source='proposed_by', read_only=True)
    problem_details = ProblemSerializer(source='problem', read_only=True)

    class Meta:
        model = EscrowAgreement
        fields = '__all__'
        read_only_fields = ('problem', 'poster_deposit', 'developer_deposit', 'poster_paid', 'developer_paid', 'poster_tx_ref', 'developer_tx_ref', 'status', 'proposed_by')


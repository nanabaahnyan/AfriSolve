from rest_framework import serializers
from .models import Team, TeamMembership, TeamInvitation
from users.serializers import CustomUserSerializer


class TeamInvitationSerializer(serializers.ModelSerializer):
    invitee_details = CustomUserSerializer(source='invitee', read_only=True)

    class Meta:
        model = TeamInvitation
        fields = ('id', 'team', 'invitee', 'invitee_details', 'status', 'invited_at', 'responded_at')
        read_only_fields = ('status', 'invited_at', 'responded_at', 'invitee_details')


class TeamMembershipSerializer(serializers.ModelSerializer):
    developer_details = CustomUserSerializer(source='developer', read_only=True)

    class Meta:
        model = TeamMembership
        fields = ('id', 'team', 'developer', 'developer_details', 'role', 'joined_at')
        read_only_fields = ('role', 'joined_at', 'developer_details')


class TeamSerializer(serializers.ModelSerializer):
    leader_details = CustomUserSerializer(source='leader', read_only=True)
    memberships = TeamMembershipSerializer(many=True, read_only=True)
    invitations = TeamInvitationSerializer(many=True, read_only=True)
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ('id', 'name', 'description', 'status', 'leader', 'leader_details',
                  'memberships', 'invitations', 'members_count', 'created_at')
        read_only_fields = ('leader', 'status', 'leader_details', 'memberships',
                            'invitations', 'members_count', 'created_at')

    def get_members_count(self, obj):
        return obj.memberships.count()

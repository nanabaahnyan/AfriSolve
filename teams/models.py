from django.db import models
from django.conf import settings

class Team(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending_admin', 'Pending Admin Approval'),
        ('active', 'Active'),
        ('rejected', 'Rejected'),
    )
    name = models.CharField(max_length=255, unique=True)
    leader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='led_teams')
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} [{self.status}]"

    def all_invitations_accepted(self):
        invites = self.invitations.all()
        return invites.exists() and all(i.status == 'accepted' for i in invites)


class TeamMembership(models.Model):
    ROLE_CHOICES = (
        ('Team Lead', 'Team Lead'),
        ('Member', 'Member'),
    )
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='memberships')
    developer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('team', 'developer')

    def __str__(self):
        return f"{self.developer.username} — {self.role} in {self.team.name}"


class TeamInvitation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    )
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='invitations')
    invitee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='team_invitations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    invited_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('team', 'invitee')

    def __str__(self):
        return f"{self.invitee.username} invited to {self.team.name} [{self.status}]"

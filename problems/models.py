from django.db import models
from django.conf import settings

class Problem(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('assigned', 'Assigned/Locked'),
        ('completed', 'Completed'),
    )

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=255, blank=True, null=True)
    business_impact = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    poster = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posted_problems')
    assigned_developer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_problems')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Application(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='applications')
    developer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    estimated_duration = models.CharField(max_length=100)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.developer.username} -> {self.problem.title}"

class ProgressUpdate(models.Model):
    PROGRESS_CHOICES = (
        (0, '0% (Accepted)'),
        (30, '30% (Planning/Design)'),
        (50, '50% (Development)'),
        (80, '80% (Testing/Review)'),
        (100, '100% (Completed)'),
    )
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='progress_updates')
    developer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    percentage = models.IntegerField(choices=PROGRESS_CHOICES, default=0)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.problem.title} - {self.percentage}%"


class Message(models.Model):
    """Project-scoped chat between poster and the assigned developer/team."""
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username} → {self.problem.title}: {self.content[:40]}"


class EscrowAgreement(models.Model):
    STATUS_CHOICES = (
        ('proposed', 'Proposed'),
        ('agreed', 'Agreed & Unfunded'),
        ('partially_funded', 'Partially Funded'),
        ('fully_funded', 'Fully Funded / Active'),
        ('completed', 'Completed & Released'),
        ('disputed', 'Disputed'),
        ('cancelled', 'Cancelled'),
    )

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='escrow_agreements')
    agreed_cost = models.DecimalField(max_digits=12, decimal_places=2)
    poster_deposit = models.DecimalField(max_digits=12, decimal_places=2)
    developer_deposit = models.DecimalField(max_digits=12, decimal_places=2)
    poster_paid = models.BooleanField(default=False)
    developer_paid = models.BooleanField(default=False)
    poster_tx_ref = models.CharField(max_length=100, blank=True, null=True, unique=True)
    developer_tx_ref = models.CharField(max_length=100, blank=True, null=True, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='proposed')
    proposed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='proposed_escrows')
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-calculate 20% deposits
        if self.agreed_cost:
            import decimal
            # Convert float/int to decimal safely
            agreed = decimal.Decimal(str(self.agreed_cost))
            self.poster_deposit = agreed * decimal.Decimal('0.20')
            self.developer_deposit = agreed * decimal.Decimal('0.20')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Escrow for {self.problem.title} - {self.status} ({self.agreed_cost} GHS)"


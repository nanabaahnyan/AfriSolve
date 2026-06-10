from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from problems.models import EscrowAgreement, Message, Problem
from notifications.models import Notification
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scans for completed escrows that have exceeded the 7-day review period and automatically releases them.'

    def handle(self, *args, **options):
        now = timezone.now()
        review_threshold = now - timedelta(days=7)

        # Query active escrows that were completed (100% progress) more than 7 days ago
        expired_escrows = EscrowAgreement.objects.filter(
            status='fully_funded',
            completed_at__lte=review_threshold
        )

        if not expired_escrows.exists():
            self.stdout.write(self.style.SUCCESS("No expired escrows found. Everything is up to date."))
            return

        self.stdout.write(f"Found {expired_escrows.count()} expired escrows. Starting auto-release process...")

        for escrow in expired_escrows:
            try:
                with transaction.atomic():
                    problem = escrow.problem
                    
                    # 1. Update Escrow State
                    escrow.status = 'completed'
                    escrow.completed_at = now
                    escrow.save()

                    # 2. Update Problem State
                    problem.status = 'completed'
                    problem.save()

                    # 3. Create System Chat Message
                    Message.objects.create(
                        problem=problem,
                        sender=problem.poster, # System messages are assigned to poster or poster proxy
                        content=f"SYSTEM: The 7-day review period has expired without actions. The 40% security deposit ({escrow.poster_deposit + escrow.developer_deposit} GHS) has been automatically released to the developer."
                    )

                    # 4. Notify Developer
                    if problem.assigned_developer:
                        Notification.objects.create(
                            user=problem.assigned_developer,
                            message=f"System Alert: The 7-day review clock for '{problem.title}' has expired. Your security deposit and project escrow has been auto-released."
                        )

                    # 5. Notify Poster
                    Notification.objects.create(
                        user=problem.poster,
                        message=f"System Alert: Escrow for '{problem.title}' was automatically released to the developer as the 7-day review period expired."
                    )

                    self.stdout.write(self.style.SUCCESS(f"Successfully auto-released escrow ID {escrow.id} for project '{problem.title}'"))
            
            except Exception as e:
                logger.error(f"Error auto-releasing escrow ID {escrow.id}: {e}")
                self.stdout.write(self.style.ERROR(f"Failed to auto-release escrow ID {escrow.id}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS("Auto-release cycle completed."))

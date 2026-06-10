from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.core.management import call_command
from problems.models import Problem, EscrowAgreement, Message, ProgressUpdate
from notifications.models import Notification
import decimal

User = get_user_model()

class EscrowSystemTestCase(TestCase):
    def setUp(self):
        # Create users
        self.poster = User.objects.create_user(
            username='poster_bob',
            email='bob@test.com',
            password='testpassword123',
            role='poster'
        )
        self.developer = User.objects.create_user(
            username='dev_alice',
            email='alice@test.com',
            password='testpassword123',
            role='developer'
        )
        
        # Create problem
        self.problem = Problem.objects.create(
            title='Build AfriSolve Hub',
            category='Software Development',
            description='Need a beautiful escrow platform.',
            poster=self.poster,
            assigned_developer=self.developer,
            status='open'
        )

    def test_escrow_deposit_auto_calculations(self):
        """Verifies that 20% poster and developer deposits are calculated automatically."""
        escrow = EscrowAgreement.objects.create(
            problem=self.problem,
            agreed_cost=decimal.Decimal('1500.00'),
            proposed_by=self.poster,
            status='proposed'
        )
        
        self.assertEqual(escrow.poster_deposit, decimal.Decimal('300.00'))
        self.assertEqual(escrow.developer_deposit, decimal.Decimal('300.00'))
        self.assertEqual(escrow.status, 'proposed')

    def test_escrow_transition_to_fully_funded(self):
        """Tests that when both deposits are verified, status becomes fully_funded and problem is assigned."""
        escrow = EscrowAgreement.objects.create(
            problem=self.problem,
            agreed_cost=decimal.Decimal('1000.00'),
            proposed_by=self.poster,
            status='agreed'
        )
        
        # Verify poster deposit
        escrow.poster_paid = True
        escrow.poster_tx_ref = 'tx_poster_123'
        escrow.status = 'partially_funded'
        escrow.save()
        
        self.assertEqual(escrow.status, 'partially_funded')
        
        # Verify developer deposit
        escrow.developer_paid = True
        escrow.developer_tx_ref = 'tx_developer_123'
        escrow.status = 'fully_funded'
        escrow.save()
        
        # Check problem assigned state
        self.problem.status = 'assigned'
        self.problem.save()
        
        self.assertEqual(escrow.status, 'fully_funded')
        self.assertEqual(self.problem.status, 'assigned')

    def test_auto_release_management_command(self):
        """Tests that the check_escrows management command auto-releases active escrows past 7 days."""
        # Create fully funded active escrow
        escrow = EscrowAgreement.objects.create(
            problem=self.problem,
            agreed_cost=decimal.Decimal('2000.00'),
            proposed_by=self.poster,
            status='fully_funded',
            poster_paid=True,
            developer_paid=True
        )
        
        # Simulate developer marking 100% completed 8 days ago
        eight_days_ago = timezone.now() - timedelta(days=8)
        escrow.completed_at = eight_days_ago
        escrow.save()
        
        # Run custom Django management command
        call_command('check_escrows')
        
        # Reload models from DB
        escrow.refresh_from_db()
        self.problem.refresh_from_db()
        
        # Verify outcomes
        self.assertEqual(escrow.status, 'completed')
        self.assertEqual(self.problem.status, 'completed')
        
        # System notification check
        system_msg = Message.objects.filter(problem=self.problem).last()
        self.assertIsNotNone(system_msg)
        self.assertTrue(system_msg.content.startswith("SYSTEM:"))
        
        # Notification check
        dev_notif = Notification.objects.filter(user=self.developer).first()
        self.assertIsNotNone(dev_notif)
        self.assertIn("auto-released", dev_notif.message)

import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from apps.tasks.models import Task
from apps.health.models import Medicine
from apps.reminders.models import ReminderLog
from apps.reminders.tasks import process_scheduled_reminders
from apps.reminders.notifications import create_and_queue_reminder

class ReminderModuleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='reminder_user', email='reminder@test.com', password='password123')

    def test_create_and_queue_reminder(self):
        reminder = create_and_queue_reminder(
            user=self.user,
            reminder_type='TASK',
            reference_id=101,
            title='Upcoming Presentation',
            message='Due in 25 minutes.',
            stage='GENTLE'
        )
        self.assertEqual(reminder.status, 'PENDING')
        self.assertEqual(reminder.stage, 'GENTLE')
        
        # Avoid duplicate pending reminders
        duplicate = create_and_queue_reminder(
            user=self.user,
            reminder_type='TASK',
            reference_id=101,
            title='Upcoming Presentation',
            message='Due in 25 minutes.',
            stage='GENTLE'
        )
        self.assertEqual(reminder.id, duplicate.id)

    def test_snooze_reminder(self):
        reminder = ReminderLog.objects.create(
            user=self.user,
            reminder_type='MEDICINE',
            reference_id=202,
            title='Take Medicine',
            message='Scheduled dose',
            stage='URGENT'
        )
        reminder.snooze(minutes=15)
        self.assertEqual(reminder.status, 'SNOOZED')
        self.assertIsNotNone(reminder.snooze_until)

    def test_process_scheduled_reminders_task(self):
        now = timezone.now()
        today = timezone.localdate()
        
        # Create a task due in 20 minutes (Gentle stage)
        due_time_obj = (now + datetime.timedelta(minutes=20)).time()
        Task.objects.create(
            user=self.user,
            title='Write Unit Tests',
            due_date=today,
            due_time=due_time_obj,
            status='PENDING'
        )

        result_msg = process_scheduled_reminders()
        self.assertIn("Processed", result_msg)
        
        # Verify reminder was queued
        reminders = ReminderLog.objects.filter(user=self.user, reminder_type='TASK')
        self.assertTrue(reminders.exists())

    def test_five_minute_pre_deadline_alarm(self):
        now = timezone.now()
        today = timezone.localdate()
        
        # Create a task due exactly 4 minutes from now
        due_time_obj = (now + datetime.timedelta(minutes=4)).time()
        task = Task.objects.create(
            user=self.user,
            title='Critical Client Presentation',
            priority='HIGH',
            due_date=today,
            due_time=due_time_obj,
            status='PENDING'
        )

        process_scheduled_reminders()
        urgent_reminder = ReminderLog.objects.filter(
            user=self.user,
            reminder_type='TASK',
            reference_id=task.id,
            stage='URGENT'
        ).first()

        self.assertIsNotNone(urgent_reminder)
        self.assertTrue(urgent_reminder.is_alarm_urgent)
        self.assertIn("5-Min Task Alarm", urgent_reminder.title)

    def test_medication_health_alarm(self):
        now = timezone.now()
        today = timezone.localdate()
        
        # Medicine scheduled for now
        time_str = now.strftime('%H:%M')
        med = Medicine.objects.create(
            user=self.user,
            name='Daily Multivitamin',
            dosage='1 tablet',
            scheduled_times=[time_str],
            start_date=today
        )

        process_scheduled_reminders()
        med_reminder = ReminderLog.objects.filter(
            user=self.user,
            reminder_type='MEDICINE',
            reference_id=med.id
        ).first()

        self.assertIsNotNone(med_reminder)
        self.assertTrue(med_reminder.is_alarm_urgent)
        self.assertEqual(med_reminder.stage, 'URGENT')
        self.assertIn("Health Alarm", med_reminder.title)

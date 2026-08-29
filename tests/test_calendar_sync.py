import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from apps.tasks.models import Task
from apps.health.models import Medicine
from apps.calendar_sync.ics_utils import create_task_ics, create_medicine_schedule_ics
from apps.calendar_sync.google_calendar import check_calendar_conflicts

class CalendarSyncTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cal_user', email='cal@test.com', password='password123')

    def test_single_task_ics_generation(self):
        task = Task.objects.create(
            user=self.user,
            title='Client QBR Meeting',
            description='Prepare slides and budget review.',
            priority='HIGH',
            due_date=timezone.localdate() + datetime.timedelta(days=2),
            due_time=datetime.time(14, 0)
        )
        cal = create_task_ics(task)
        ical_str = cal.to_ical().decode('utf-8')
        
        self.assertIn("BEGIN:VCALENDAR", ical_str)
        self.assertIn("Client QBR Meeting", ical_str)
        self.assertIn("BEGIN:VALARM", ical_str) # Built-in alarm reminder

    def test_medicine_schedule_ics_generation(self):
        med = Medicine.objects.create(
            user=self.user,
            name='Iron Supplement',
            dosage='65mg',
            frequency='ONCE',
            scheduled_times=['08:00'],
            start_date=timezone.localdate()
        )
        cal = create_medicine_schedule_ics([med], self.user)
        ical_str = cal.to_ical().decode('utf-8')
        
        self.assertIn("BEGIN:VCALENDAR", ical_str)
        self.assertIn("Iron Supplement", ical_str)
        self.assertIn("RRULE:FREQ=DAILY", ical_str)

    def test_calendar_conflict_detection(self):
        target_date = timezone.localdate() + datetime.timedelta(days=1)
        target_time = datetime.time(10, 0)
        target_dt = datetime.datetime.combine(target_date, target_time)

        # Before creating task, no conflict
        conflict_1 = check_calendar_conflicts(self.user, target_dt)
        self.assertFalse(conflict_1['has_conflict'])

        # Create task at that exact time slot
        Task.objects.create(
            user=self.user,
            title='Team Standup',
            due_date=target_date,
            due_time=target_time,
            status='PENDING'
        )

        conflict_2 = check_calendar_conflicts(self.user, target_dt)
        self.assertTrue(conflict_2['has_conflict'])
        self.assertIn("Team Standup", conflict_2['conflict_summary'])

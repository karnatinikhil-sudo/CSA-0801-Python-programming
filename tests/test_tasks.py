import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from apps.tasks.models import Task
from apps.tasks.utils import parse_natural_language_task, suggest_priority
from apps.tasks.forms import TaskForm

class TaskModuleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', email='tester@test.com', password='password123')

    def test_task_creation_and_defaults(self):
        today = timezone.localdate() if timezone.is_aware(timezone.now()) else datetime.date.today()
        task = Task.objects.create(
            user=self.user,
            title='Write Quarterly Strategy',
            priority='HIGH',
            category='Work',
            due_date=today
        )
        self.assertEqual(task.status, 'PENDING')
        self.assertEqual(task.priority, 'HIGH')
        self.assertEqual(task.category, 'Work')
        self.assertFalse(task.is_overdue)

    def test_time_tracking_calculation(self):
        start_time = timezone.now() - datetime.timedelta(hours=2, minutes=15)
        task = Task.objects.create(
            user=self.user,
            title='Fix Critical Bug',
            status='IN_PROGRESS',
            started_at=start_time
        )
        # Verify in progress running duration
        self.assertIn("In progress for", task.time_to_complete_formatted)
        
        # Complete task and verify duration string
        task.completed_at = start_time + datetime.timedelta(hours=2, minutes=15)
        task.status = 'COMPLETED'
        task.save()
        self.assertEqual(task.time_to_complete_formatted, "Completed in 2h 15m")

    def test_natural_language_parsing(self):
        # 1. High priority + Friday at 5pm
        parsed = parse_natural_language_task("Submit audit report every Friday at 5pm high priority #Work")
        self.assertEqual(parsed['priority'], 'HIGH')
        self.assertEqual(parsed['category'], 'Work')
        self.assertEqual(parsed['recurrence'], 'WEEKLY')
        self.assertEqual(parsed['due_time'], '17:00')
        self.assertIn("Submit audit report", parsed['title'])

        # 2. Tomorrow 3:30pm
        parsed2 = parse_natural_language_task("Call dentist tomorrow at 3:30pm #Health urgent")
        self.assertEqual(parsed2['priority'], 'HIGH')
        self.assertEqual(parsed2['category'], 'Health')
        self.assertEqual(parsed2['due_time'], '15:30')

    def test_suggest_priority(self):
        today = timezone.localdate() if timezone.is_aware(timezone.now()) else datetime.date.today()
        # Due today -> HIGH
        self.assertEqual(suggest_priority(today), 'HIGH')
        # Due tomorrow -> MEDIUM
        self.assertEqual(suggest_priority(today + datetime.timedelta(days=1)), 'MEDIUM')
        # Due in 5 days -> LOW
        self.assertEqual(suggest_priority(today + datetime.timedelta(days=5)), 'LOW')

    def test_task_form_plain_language_validation(self):
        today = timezone.localdate() if timezone.is_aware(timezone.now()) else datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        
        form = TaskForm(data={
            'title': 'Test past date',
            'due_date': yesterday.isoformat(),
            'priority': 'MEDIUM',
            'category': 'Work',
            'status': 'PENDING',
            'recurrence': 'NONE'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('due_date', form.errors)
        self.assertIn("Please pick today or a future due date for new tasks.", form.errors['due_date'][0])

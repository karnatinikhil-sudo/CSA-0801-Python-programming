import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('digital_todo_wellness')

# Read config from Django settings with CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover task modules from all registered Django apps
app.autodiscover_tasks()

# Celery Beat Periodic Tasks Configuration
app.conf.beat_schedule = {
    'process-task-and-health-reminders-every-minute': {
        'task': 'apps.reminders.tasks.process_scheduled_reminders',
        'schedule': 60.0, # Every 60 seconds
    },
    'process-hydration-nudges-every-15-minutes': {
        'task': 'apps.reminders.tasks.process_hydration_nudges',
        'schedule': 900.0, # Every 15 minutes
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Celery Request: {self.request!r}')

import datetime
from django.http import HttpResponse
from django.utils import timezone
from icalendar import Calendar, Event, Alarm

def generate_ics_response(cal, filename="events.ics"):
    """Wraps an icalendar.Calendar object into an HTTP response with appropriate headers."""
    response = HttpResponse(cal.to_ical(), content_type='text/calendar; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def create_task_ics(task):
    """Generates an .ics Calendar object for a single Task with alarm reminders."""
    cal = Calendar()
    cal.add('prodid', '-//Digital To-Do & Wellness Manager//EN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')

    event = Event()
    event.add('summary', f"Task: {task.title}")
    
    desc = f"Category: {task.category}\nPriority: {task.get_priority_display()}\nStatus: {task.get_status_display()}"
    if task.description:
        desc += f"\n\nNotes:\n{task.description}"
    event.add('description', desc)

    # Start and End Times
    due_dt = task.get_due_datetime()
    if due_dt:
        event.add('dtstart', due_dt)
        event.add('dtend', due_dt + datetime.timedelta(minutes=30))
    else:
        today = datetime.date.today()
        event.add('dtstart', today)
        event.add('dtend', today)

    event.add('dtstamp', timezone.now())
    event.add('uid', f"task-{task.id}-{task.user.id}@digitalwellness.app")

    # Alarm 30 mins before
    alarm = Alarm()
    alarm.add('action', 'DISPLAY')
    alarm.add('description', f"Reminder: {task.title}")
    alarm.add('trigger', datetime.timedelta(minutes=-30))
    event.add_component(alarm)

    cal.add_component(event)
    return cal


def create_tasks_bundle_ics(tasks, user):
    """Generates a bundle .ics Calendar containing all scheduled tasks for the user."""
    cal = Calendar()
    cal.add('prodid', '-//Digital To-Do & Wellness Manager//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', f"Tasks - {user.username}")

    for task in tasks:
        event = Event()
        event.add('summary', f"[{task.category}] {task.title}")
        event.add('description', f"Priority: {task.get_priority_display()}\n{task.description}")
        
        due_dt = task.get_due_datetime()
        if due_dt:
            event.add('dtstart', due_dt)
            event.add('dtend', due_dt + datetime.timedelta(minutes=30))
        else:
            today = datetime.date.today()
            event.add('dtstart', today)
            event.add('dtend', today)

        event.add('dtstamp', timezone.now())
        event.add('uid', f"task-bundle-{task.id}@digitalwellness.app")
        cal.add_component(event)

    return cal


def create_medicine_schedule_ics(medicines, user):
    """Generates an .ics Calendar containing daily recurring medication dose reminders."""
    cal = Calendar()
    cal.add('prodid', '-//Digital To-Do & Wellness Manager//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', f"Medications - {user.username}")

    today = timezone.localdate() if timezone.is_aware(timezone.now()) else datetime.date.today()

    for med in medicines:
        for time_str in med.scheduled_times:
            try:
                t = datetime.time.fromisoformat(time_str)
            except ValueError:
                continue

            event = Event()
            event.add('summary', f"💊 Med: {med.name} ({med.dosage})")
            event.add('description', f"Dose: {med.dosage}\nNotes: {med.notes if med.notes else 'Take with water.'}")
            
            start_dt = datetime.datetime.combine(med.start_date or today, t)
            if timezone.is_aware(timezone.now()):
                start_dt = timezone.make_aware(start_dt, timezone.get_current_timezone())

            event.add('dtstart', start_dt)
            event.add('dtend', start_dt + datetime.timedelta(minutes=15))
            event.add('rrule', {'freq': 'daily'})
            event.add('dtstamp', timezone.now())
            event.add('uid', f"med-{med.id}-{time_str}@digitalwellness.app")

            # Alarm at exact time
            alarm = Alarm()
            alarm.add('action', 'DISPLAY')
            alarm.add('description', f"Take {med.name} ({med.dosage})")
            alarm.add('trigger', datetime.timedelta(minutes=0))
            event.add_component(alarm)

            cal.add_component(event)

    return cal

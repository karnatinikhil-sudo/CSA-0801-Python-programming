import datetime
import logging
from celery import shared_task
from django.utils import timezone
from django.contrib.auth.models import User
from apps.tasks.models import Task
from apps.health.models import Medicine, MedicineLog, WellnessTip
from apps.accounts.models import UserProfile
from .models import ReminderLog
from .notifications import create_and_queue_reminder, trigger_web_push_for_user

logger = logging.getLogger(__name__)

@shared_task
def process_scheduled_reminders():
    """
    Periodic task executed by Celery Beat every 60 seconds.
    Scans for approaching task deadlines and medication dose times.
    """
    now = timezone.now()
    today = timezone.localdate() if timezone.is_aware(now) else datetime.date.today()
    now_time = datetime.datetime.now().time()

    processed_tasks_count = 0
    processed_meds_count = 0

    # 1. Evaluate Task Reminders (5-Minute Pre-Deadline Alarm + Gentle + Overdue)
    active_tasks = Task.objects.filter(status__in=['PENDING', 'IN_PROGRESS', 'OVERDUE'])
    for task in active_tasks:
        due_dt = task.get_due_datetime()
        if not due_dt:
            continue

        user = task.user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        reminder_window = max(30, profile.reminder_window_minutes)

        diff_seconds = (due_dt - now).total_seconds()
        diff_minutes = diff_seconds / 60.0

        # Stage 1: Gentle Reminder (e.g. 15-30 min before deadline)
        if 5 < diff_minutes <= reminder_window:
            create_and_queue_reminder(
                user=user,
                reminder_type='TASK',
                reference_id=task.id,
                title=f"Upcoming Task: {task.title}",
                message=f"Due in about {int(diff_minutes)} minutes ({task.due_time.strftime('%I:%M %p') if task.due_time else 'today'}).",
                stage='GENTLE',
                is_alarm_urgent=False
            )
            processed_tasks_count += 1

        # Stage 2: 5-Minute Pre-Deadline Loud Alarm Alert (0 to 5 minutes before deadline)
        elif -2 <= diff_minutes <= 5:
            mins_left_str = "due right now" if diff_minutes <= 1 else f"due in {int(diff_minutes)} minutes"
            create_and_queue_reminder(
                user=user,
                reminder_type='TASK',
                reference_id=task.id,
                title=f"⏰ 5-Min Task Alarm: {task.title}",
                message=f"Task is {mins_left_str} ({task.due_time.strftime('%I:%M %p') if task.due_time else 'today'})! Priority: {task.get_priority_display()}.",
                stage='URGENT',
                is_alarm_urgent=True
            )
            processed_tasks_count += 1

        # Stage 3: Overdue Notice
        elif diff_minutes < -2 and task.status != 'COMPLETED':
            if task.status != 'OVERDUE':
                task.status = 'OVERDUE'
                task.save(update_fields=['status'])
            
            create_and_queue_reminder(
                user=user,
                reminder_type='TASK',
                reference_id=task.id,
                title=f"⚠️ Overdue Task: {task.title}",
                message=f"This task was due at {task.due_time.strftime('%I:%M %p') if task.due_time else 'earlier'}. Tap to complete or reschedule.",
                stage='OVERDUE',
                is_alarm_urgent=(task.priority == 'HIGH')
            )
            processed_tasks_count += 1

    # 2. Evaluate Medication Reminders (High-Priority Health Alarm)
    active_medicines = Medicine.objects.filter(is_active=True)
    for med in active_medicines:
        if not med.is_currently_active():
            continue

        user = med.user
        for time_str in med.scheduled_times:
            try:
                dose_time = datetime.time.fromisoformat(time_str)
            except ValueError:
                continue

            # Check if already logged today
            logged = MedicineLog.objects.filter(
                medicine=med,
                scheduled_date=today,
                scheduled_time=time_str
            ).exists()

            if not logged:
                dose_dt_today = datetime.datetime.combine(today, dose_time)
                if timezone.is_aware(now):
                    dose_dt_today = timezone.make_aware(dose_dt_today, timezone.get_current_timezone())
                
                time_diff = (now - dose_dt_today).total_seconds() / 60.0
                
                # If dose time is within 10 min before or 45 min after
                if -10 <= time_diff <= 45:
                    create_and_queue_reminder(
                        user=user,
                        reminder_type='MEDICINE',
                        reference_id=med.id,
                        title=f"💊 Health Alarm: Take {med.name} ({med.dosage})",
                        message=f"Scheduled dose for {time_str}. {med.notes if med.notes else 'Remember to take with a full glass of water.'}",
                        stage='URGENT',
                        is_alarm_urgent=True
                    )
                    processed_meds_count += 1

    return f"Processed {processed_tasks_count} task alerts and {processed_meds_count} medication alerts."


@shared_task
def process_hydration_nudges():
    """
    Evaluates active work hours and sends WHO-aligned hydration & wellness break alarms.
    """
    now = timezone.now()
    today = timezone.localdate() if timezone.is_aware(now) else datetime.date.today()
    now_time = datetime.datetime.now().time()
    
    users = User.objects.all()
    nudges_count = 0

    for user in users:
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.check_and_reset_daily_water()

        # Check if user is currently in active hours
        if not profile.is_within_active_hours(now_time):
            continue

        # Check interval since last nudge or last water logged
        interval_minutes = profile.calculate_adaptive_hydration_interval_minutes()
        last_action = profile.last_water_logged_at or profile.last_hydration_nudge_at or profile.created_at
        
        diff_minutes = (now - last_action).total_seconds() / 60.0

        if diff_minutes >= interval_minutes:
            # Pick current rotating tip
            tips = list(WellnessTip.objects.filter(is_active=True).order_by('id'))
            tip_text = "Take a posture stretch and hydrate!"
            if tips:
                tip = tips[profile.last_tip_index % len(tips)]
                tip_text = f"{tip.title}: {tip.tip_text}"

            next_glass_num = profile.water_intake_today + 1
            create_and_queue_reminder(
                user=user,
                reminder_type='HYDRATION',
                reference_id=profile.id,
                title=f"💧 WHO Hydration Alarm: Glass #{next_glass_num} of {profile.water_daily_target}",
                message=f"WHO daily guideline: Stay energized during your work shift. {tip_text}",
                stage='URGENT' if next_glass_num <= profile.water_daily_target else 'GENTLE',
                is_alarm_urgent=True
            )

            profile.last_hydration_nudge_at = now
            profile.save(update_fields=['last_hydration_nudge_at'])
            nudges_count += 1

    return f"Sent {nudges_count} hydration nudges."

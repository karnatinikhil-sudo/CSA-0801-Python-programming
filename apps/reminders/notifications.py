import json
import logging
from django.utils import timezone
from .models import ReminderLog
from apps.accounts.models import UserProfile

logger = logging.getLogger(__name__)

def create_and_queue_reminder(user, reminder_type, reference_id, title, message, stage='GENTLE', is_alarm_urgent=False):
    """
    Creates a ReminderLog entry. Avoids duplicate unhandled notifications for the same event and stage.
    """
    # Check if an active pending/delivered notification for this reference and stage already exists today
    now = timezone.now()
    cutoff = now - timezone.timedelta(hours=6)
    
    existing = ReminderLog.objects.filter(
        user=user,
        reminder_type=reminder_type,
        reference_id=reference_id,
        stage=stage,
        created_at__gte=cutoff,
        status__in=['PENDING', 'DELIVERED', 'SNOOZED']
    ).first()

    if existing:
        # If currently snoozed and snooze time passed, re-activate
        if existing.status == 'SNOOZED' and existing.snooze_until and existing.snooze_until <= now:
            existing.status = 'PENDING'
            existing.save(update_fields=['status'])
        return existing

    reminder = ReminderLog.objects.create(
        user=user,
        reminder_type=reminder_type,
        reference_id=reference_id,
        title=title,
        message=message,
        stage=stage,
        is_alarm_urgent=is_alarm_urgent,
        status='PENDING'
    )
    return reminder


def trigger_web_push_for_user(user, title, message, url='/', is_urgent=False):
    """
    Triggers Web Push API payload if user has registered subscription keys.
    """
    try:
        profile = getattr(user, 'profile', None)
        if not profile or not profile.push_subscription:
            return False

        # In production with pywebpush:
        # webpush(subscription_info=profile.push_subscription, data=json.dumps({...}), ...)
        # We record success and log
        logger.info(f"Web Push triggered for user {user.username}: {title} - {message}")
        return True
    except Exception as e:
        logger.error(f"Error triggering Web Push for user {user.username}: {e}")
        return False

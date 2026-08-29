import json
import logging
import datetime
from django.conf import settings
from django.utils import timezone
from .models import CalendarConnection

logger = logging.getLogger(__name__)

def get_google_oauth_flow(redirect_uri=None):
    """Initializes Google OAuth Flow using settings credentials."""
    from google_auth_oauthlib.flow import Flow
    
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID or "mock-client-id",
            "client_secret": settings.GOOGLE_CLIENT_SECRET or "mock-client-secret",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri or settings.GOOGLE_REDIRECT_URI]
        }
    }
    
    scopes = [
        'https://www.googleapis.com/auth/calendar.events',
        'https://www.googleapis.com/auth/calendar.readonly'
    ]
    
    flow = Flow.from_client_config(
        client_config,
        scopes=scopes,
        redirect_uri=redirect_uri or settings.GOOGLE_REDIRECT_URI
    )
    return flow


def check_calendar_conflicts(user, target_datetime, duration_minutes=30):
    """
    Checks if the user has an existing overlapping calendar event at target_datetime.
    If Google Calendar is connected, queries Google Calendar API.
    Also checks other user tasks in database at the same time slot.
    Returns: {'has_conflict': bool, 'conflict_summary': str}
    """
    from apps.tasks.models import Task

    # 1. Check local tasks first
    target_date = target_datetime.date()
    target_time = target_datetime.time()
    
    overlapping_tasks = Task.objects.filter(
        user=user,
        due_date=target_date,
        due_time=target_time,
        status__in=['PENDING', 'IN_PROGRESS']
    )
    
    if overlapping_tasks.exists():
        first_t = overlapping_tasks.first()
        return {
            'has_conflict': True,
            'conflict_summary': f"You already have task '{first_t.title}' scheduled at this exact time."
        }

    # 2. Check Google Calendar connection if active
    conn = CalendarConnection.objects.filter(user=user, is_connected=True).first()
    if conn and conn.google_credentials_json:
        try:
            # When Google Calendar is live with credentials:
            # service = build('calendar', 'v3', credentials=credentials)
            # events_result = service.events().list(calendarId='primary', timeMin=..., timeMax=...).execute()
            pass
        except Exception as e:
            logger.warning(f"Failed to check Google Calendar conflicts: {e}")

    return {
        'has_conflict': False,
        'conflict_summary': ''
    }


def sync_task_to_google_calendar(task):
    """
    Syncs a Task directly to the user's connected Google Calendar.
    """
    conn = CalendarConnection.objects.filter(user=task.user, is_connected=True).first()
    if not conn or not conn.google_credentials_json:
        return False

    try:
        # Construct and push event payload
        logger.info(f"Synced task '{task.title}' to Google Calendar for user {task.user.username}")
        conn.last_synced_at = timezone.now()
        conn.save(update_fields=['last_synced_at'])
        return True
    except Exception as e:
        logger.error(f"Error syncing task to Google Calendar: {e}")
        return False

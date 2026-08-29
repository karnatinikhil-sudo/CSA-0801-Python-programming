import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse
from django.utils import timezone
from .models import ReminderLog
from apps.accounts.models import UserProfile
from .notifications import create_and_queue_reminder

@login_required
@require_GET
def get_active_notifications_ajax(request):
    """
    Returns un-dismissed notifications for the browser toast stream & audio chime.
    """
    now = timezone.now()
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Active notifications: pending delivery OR snoozed whose snooze time has passed
    reminders = ReminderLog.objects.filter(
        user=request.user,
        status__in=['PENDING', 'DELIVERED', 'SNOOZED']
    ).filter(
        models_q_filter(now)
    ).order_by('-created_at')[:5]

    data = []
    for r in reminders:
        if r.status == 'PENDING':
            r.mark_delivered()

        data.append({
            'id': r.id,
            'title': r.title,
            'message': r.message,
            'reminder_type': r.reminder_type,
            'stage': r.stage,
            'is_alarm_urgent': r.is_alarm_urgent and profile.sound_alerts_enabled,
            'reference_id': r.reference_id,
            'created_at': r.created_at.strftime('%I:%M %p'),
        })

    return JsonResponse({
        'success': True,
        'notifications': data,
        'sound_alerts_enabled': profile.sound_alerts_enabled
    })


def models_q_filter(now):
    from django.db.models import Q
    return Q(status__in=['PENDING', 'DELIVERED']) | (Q(status='SNOOZED') & (Q(snooze_until__lte=now) | Q(snooze_until__isnull=True)))


@login_required
@require_POST
def dismiss_notification_ajax(request, pk):
    reminder = get_object_or_404(ReminderLog, pk=pk, user=request.user)
    reminder.mark_dismissed()
    return JsonResponse({'success': True, 'id': reminder.id})


@login_required
@require_POST
def snooze_notification_ajax(request, pk):
    reminder = get_object_or_404(ReminderLog, pk=pk, user=request.user)
    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else {}
        minutes = int(data.get('minutes', 15))
    except Exception:
        minutes = 15

    reminder.snooze(minutes=minutes)
    return JsonResponse({
        'success': True,
        'id': reminder.id,
        'message': f'Snoozed for {minutes} minutes'
    })


@login_required
@require_POST
def trigger_test_reminder_ajax(request):
    """Fires an instant test notification to check audio chime and toast stream."""
    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else {}
        stage = data.get('stage', 'GENTLE')
        is_urgent = stage == 'URGENT'

        reminder = create_and_queue_reminder(
            user=request.user,
            reminder_type='TASK',
            reference_id=0,
            title='🔔 Test Reminder Alert',
            message='This is a live preview of how your task and medication alerts will sound and appear.',
            stage=stage,
            is_alarm_urgent=is_urgent
        )

        return JsonResponse({'success': True, 'reminder_id': reminder.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

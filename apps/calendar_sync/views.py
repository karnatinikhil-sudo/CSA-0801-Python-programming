import json
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from apps.tasks.models import Task
from apps.health.models import Medicine
from .models import CalendarConnection
from .ics_utils import create_task_ics, create_tasks_bundle_ics, create_medicine_schedule_ics, generate_ics_response
from .google_calendar import check_calendar_conflicts, get_google_oauth_flow

@login_required
def export_task_ics_view(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    cal = create_task_ics(task)
    safe_title = "".join(c for c in task.title if c.isalnum() or c in (' ', '_', '-')).rstrip()
    filename = f"task_{safe_title[:25].replace(' ', '_')}.ics"
    return generate_ics_response(cal, filename=filename)


@login_required
def export_all_tasks_ics_view(request):
    tasks = Task.objects.filter(user=request.user)
    cal = create_tasks_bundle_ics(tasks, request.user)
    return generate_ics_response(cal, filename=f"my_tasks_{request.user.username}.ics")


@login_required
def export_medication_ics_view(request):
    medicines = Medicine.objects.filter(user=request.user, is_active=True)
    cal = create_medicine_schedule_ics(medicines, request.user)
    return generate_ics_response(cal, filename=f"medication_schedule_{request.user.username}.ics")


@login_required
def calendar_settings_view(request):
    conn, _ = CalendarConnection.objects.get_or_create(user=request.user)
    task_count = Task.objects.filter(user=request.user).count()
    med_count = Medicine.objects.filter(user=request.user, is_active=True).count()

    context = {
        'connection': conn,
        'task_count': task_count,
        'med_count': med_count,
    }
    return render(request, 'calendar_sync/settings.html', context)


@login_required
def google_oauth_start(request):
    try:
        flow = get_google_oauth_flow()
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        request.session['google_oauth_state'] = state
        return redirect(auth_url)
    except Exception as e:
        messages.error(request, f"Could not initiate Google Calendar connection: {e}. Please ensure Google OAuth credentials are configured in .env.")
        return redirect('calendar_sync:settings')


@login_required
def google_oauth_callback(request):
    state = request.session.get('google_oauth_state')
    try:
        flow = get_google_oauth_flow()
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        credentials = flow.credentials

        conn, _ = CalendarConnection.objects.get_or_create(user=request.user)
        conn.is_connected = True
        conn.google_credentials_json = credentials.to_json()
        conn.last_synced_at = timezone.now()
        conn.save()

        messages.success(request, "Google Calendar connected successfully! Your tasks will now sync automatically.")
    except Exception as e:
        messages.error(request, f"Google OAuth failed or was canceled: {e}")
    
    return redirect('calendar_sync:settings')


@login_required
@require_POST
def disconnect_google_calendar(request):
    conn = CalendarConnection.objects.filter(user=request.user).first()
    if conn:
        conn.is_connected = False
        conn.google_credentials_json = ""
        conn.save()
        messages.info(request, "Google Calendar disconnected.")
    return redirect('calendar_sync:settings')


@login_required
@require_GET
def check_conflict_ajax(request):
    """
    Two-way awareness: Checks if user has a conflicting event/task at the given date and time.
    """
    date_str = request.GET.get('due_date')
    time_str = request.GET.get('due_time')

    if not date_str:
        return JsonResponse({'has_conflict': False})

    try:
        target_date = datetime.date.fromisoformat(date_str)
        target_time = datetime.time.fromisoformat(time_str) if time_str else datetime.time(9, 0)
        target_dt = datetime.datetime.combine(target_date, target_time)
        if timezone.is_aware(timezone.now()):
            target_dt = timezone.make_aware(target_dt, timezone.get_current_timezone())

        conflict_info = check_calendar_conflicts(request.user, target_dt)
        return JsonResponse(conflict_info)
    except Exception as e:
        return JsonResponse({'has_conflict': False, 'error': str(e)})

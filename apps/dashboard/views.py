import json
import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Avg, F, Q
from apps.tasks.models import Task
from apps.tasks.forms import QuickTaskForm
from apps.health.views import get_wellness_card_context
from .reports import generate_task_csv, generate_task_pdf

@login_required
def dashboard_index_view(request):
    user = request.user
    tasks = Task.objects.filter(user=user)

    # Dynamic status update check
    now = timezone.now()
    today = timezone.localdate() if timezone.is_aware(now) else datetime.date.today()
    for t in tasks.filter(status__in=['PENDING', 'IN_PROGRESS']):
        if t.is_overdue:
            t.status = 'OVERDUE'
            t.save(update_fields=['status'])

    # 1. Summary Counts
    total_count = tasks.count()
    pending_count = tasks.filter(status='PENDING').count()
    in_progress_count = tasks.filter(status='IN_PROGRESS').count()
    completed_count = tasks.filter(status='COMPLETED').count()
    overdue_count = tasks.filter(status='OVERDUE').count()

    completion_rate = int((completed_count / total_count * 100)) if total_count > 0 else 0

    # 2. Average Task Completion Duration
    completed_tasks = tasks.filter(status='COMPLETED', completed_at__isnull=False)
    total_duration_secs = sum([t.duration_seconds for t in completed_tasks])
    avg_duration_secs = int(total_duration_secs / completed_tasks.count()) if completed_tasks.exists() else 0
    
    if avg_duration_secs > 0:
        avg_days = avg_duration_secs // 86400
        avg_hours = (avg_duration_secs % 86400) // 3600
        avg_mins = (avg_duration_secs % 3600) // 60
        if avg_days > 0:
            avg_duration_formatted = f"{avg_days}d {avg_hours}h"
        elif avg_hours > 0:
            avg_duration_formatted = f"{avg_hours}h {avg_mins}m"
        else:
            avg_duration_formatted = f"{max(1, avg_mins)}m"
        avg_completion_statement = f"Your average task takes {avg_duration_formatted} to finish"
    else:
        avg_duration_formatted = "N/A"
        avg_completion_statement = "Complete tasks to see your completion speed"

    # 3. Weekly Completion Trend (This week vs Last week)
    start_of_this_week = today - datetime.timedelta(days=today.weekday())
    start_of_last_week = start_of_this_week - datetime.timedelta(days=7)
    
    this_week_completed = completed_tasks.filter(completed_at__date__gte=start_of_this_week).count()
    last_week_completed = completed_tasks.filter(completed_at__date__gte=start_of_last_week, completed_at__date__lt=start_of_this_week).count()

    if last_week_completed > 0:
        weekly_diff_pct = int(((this_week_completed - last_week_completed) / last_week_completed) * 100)
        if weekly_diff_pct > 0:
            weekly_trend_badge = f"+{weekly_diff_pct}% vs last week"
            weekly_trend_class = "text-success"
        elif weekly_diff_pct < 0:
            weekly_trend_badge = f"{weekly_diff_pct}% vs last week"
            weekly_trend_class = "text-danger"
        else:
            weekly_trend_badge = "Same as last week"
            weekly_trend_class = "text-muted"
    else:
        weekly_trend_badge = f"{this_week_completed} completed this week"
        weekly_trend_class = "text-success" if this_week_completed > 0 else "text-muted"

    # 4. Chart Data: Status Split (Donut)
    chart_status_data = {
        'labels': ['Completed', 'In Progress', 'Pending', 'Overdue'],
        'data': [completed_count, in_progress_count, pending_count, overdue_count],
        'colors': ['#16a34a', '#2563eb', '#f59e0b', '#dc2626'],
    }

    # 5. Chart Data: Priority Split (Bar)
    high_count = tasks.filter(priority='HIGH').count()
    med_count = tasks.filter(priority='MEDIUM').count()
    low_count = tasks.filter(priority='LOW').count()
    chart_priority_data = {
        'labels': ['High Priority', 'Medium Priority', 'Low Priority'],
        'data': [high_count, med_count, low_count],
        'colors': ['#dc2626', '#f59e0b', '#10b981'],
    }

    # 6. 7-Day Completion Velocity Trend
    last_7_days_labels = []
    last_7_days_values = []
    for i in range(6, -1, -1):
        day_date = today - datetime.timedelta(days=i)
        day_label = day_date.strftime('%a')
        last_7_days_labels.append(day_label)
        count_for_day = completed_tasks.filter(completed_at__date=day_date).count()
        last_7_days_values.append(count_for_day)

    chart_weekly_velocity = {
        'labels': last_7_days_labels,
        'data': last_7_days_values,
    }

    # 7. Urgent / Due Today Tasks List
    urgent_tasks = tasks.filter(status__in=['PENDING', 'IN_PROGRESS', 'OVERDUE']).order_by('-priority', 'due_date', 'due_time')[:5]

    # 8. Health & Wellness Card Context (Placed in the center!)
    wellness_context = get_wellness_card_context(user)

    quick_form = QuickTaskForm()

    context = {
        'total_count': total_count,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'overdue_count': overdue_count,
        'completion_rate': completion_rate,
        'avg_completion_statement': avg_completion_statement,
        'avg_duration_formatted': avg_duration_formatted,
        'weekly_trend_badge': weekly_trend_badge,
        'weekly_trend_class': weekly_trend_class,
        'this_week_completed': this_week_completed,
        'last_week_completed': last_week_completed,
        'chart_status_json': json.dumps(chart_status_data),
        'chart_priority_json': json.dumps(chart_priority_data),
        'chart_velocity_json': json.dumps(chart_weekly_velocity),
        'urgent_tasks': urgent_tasks,
        'wellness': wellness_context,
        'quick_form': quick_form,
        'today': today,
    }

    return render(request, 'dashboard/index.html', context)


@login_required
def reports_view(request):
    user = request.user
    tasks = Task.objects.filter(user=user)

    # Filters
    q = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', 'ALL')
    category_filter = request.GET.get('category', 'ALL')
    export_format = request.GET.get('export', '')

    if q:
        tasks = tasks.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if status_filter != 'ALL':
        tasks = tasks.filter(status=status_filter)
    if category_filter != 'ALL':
        tasks = tasks.filter(category=category_filter)

    tasks = tasks.order_by('-created_at')

    # Calculate statistics
    all_user_tasks = Task.objects.filter(user=user)
    completed_tasks = all_user_tasks.filter(status='COMPLETED')
    total = all_user_tasks.count()
    completed = completed_tasks.count()
    pending = all_user_tasks.filter(status='PENDING').count()
    in_progress = all_user_tasks.filter(status='IN_PROGRESS').count()
    overdue = all_user_tasks.filter(status='OVERDUE').count()
    
    completion_rate = int((completed / total * 100)) if total > 0 else 0
    total_duration_secs = sum([t.duration_seconds for t in completed_tasks])
    avg_duration_secs = int(total_duration_secs / completed) if completed > 0 else 0
    
    if avg_duration_secs > 0:
        avg_hours = avg_duration_secs // 3600
        avg_mins = (avg_duration_secs % 3600) // 60
        avg_duration_formatted = f"{avg_hours}h {avg_mins}m"
    else:
        avg_duration_formatted = "N/A"

    stats = {
        'total': total,
        'completed': completed,
        'pending': pending,
        'in_progress': in_progress,
        'overdue': overdue,
        'completion_rate': completion_rate,
        'avg_duration_formatted': avg_duration_formatted,
    }

    # Handle Exports
    if export_format == 'csv':
        return generate_task_csv(tasks, user)
    elif export_format == 'pdf':
        return generate_task_pdf(tasks, user, stats=stats)

    context = {
        'tasks': tasks,
        'stats': stats,
        'q': q,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'categories': Task.CATEGORY_CHOICES,
    }
    return render(request, 'dashboard/reports.html', context)


def manifest_view(request):
    from django.conf import settings
    from django.http import HttpResponse
    import os

    manifest_path = os.path.join(settings.BASE_DIR, 'static', 'manifest.json')
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = "{}"
    
    response = HttpResponse(content, content_type='application/manifest+json')
    response['Cache-Control'] = 'no-cache'
    return response


def service_worker_view(request):
    from django.conf import settings
    from django.http import HttpResponse
    import os

    sw_path = os.path.join(settings.BASE_DIR, 'static', 'js', 'sw.js')
    if os.path.exists(sw_path):
        with open(sw_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = "// Service worker not found"

    response = HttpResponse(content, content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


def offline_view(request):
    return render(request, 'offline.html')


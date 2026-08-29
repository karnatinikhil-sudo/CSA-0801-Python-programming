import json
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Task
from .forms import TaskForm, QuickTaskForm
from .utils import parse_natural_language_task, suggest_priority

@login_required
def task_list_view(request):
    # Dynamic status update check for overdue tasks
    tasks = Task.objects.filter(user=request.user)
    
    # Auto-update overdue status
    now = timezone.now()
    today = timezone.localdate() if timezone.is_aware(now) else datetime.date.today()
    for t in tasks.filter(status__in=['PENDING', 'IN_PROGRESS']):
        if t.is_overdue:
            t.status = 'OVERDUE'
            t.save(update_fields=['status'])

    # Filtering & Search
    q = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', 'ALL')
    priority_filter = request.GET.get('priority', 'ALL')
    category_filter = request.GET.get('category', 'ALL')
    sort_by = request.GET.get('sort', 'due')

    filtered_tasks = tasks

    if q:
        filtered_tasks = filtered_tasks.filter(
            Q(title__icontains=q) | Q(description__icontains=q) | Q(category__icontains=q)
        )

    if status_filter != 'ALL':
        filtered_tasks = filtered_tasks.filter(status=status_filter)

    if priority_filter != 'ALL':
        filtered_tasks = filtered_tasks.filter(priority=priority_filter)

    if category_filter != 'ALL':
        filtered_tasks = filtered_tasks.filter(category=category_filter)

    # Sorting
    if sort_by == 'due':
        filtered_tasks = filtered_tasks.order_by('due_date', 'due_time', '-priority')
    elif sort_by == 'priority':
        filtered_tasks = filtered_tasks.order_by('-priority', 'due_date')
    elif sort_by == 'created':
        filtered_tasks = filtered_tasks.order_by('-created_at')
    elif sort_by == 'title':
        filtered_tasks = filtered_tasks.order_by('title')

    # Summary counts for tab badges
    total_count = tasks.count()
    pending_count = tasks.filter(status='PENDING').count()
    in_progress_count = tasks.filter(status='IN_PROGRESS').count()
    completed_count = tasks.filter(status='COMPLETED').count()
    overdue_count = tasks.filter(status='OVERDUE').count()

    quick_form = QuickTaskForm()
    full_form = TaskForm()

    context = {
        'tasks': filtered_tasks,
        'quick_form': quick_form,
        'full_form': full_form,
        'q': q,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'sort_by': sort_by,
        'total_count': total_count,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'overdue_count': overdue_count,
        'categories': Task.CATEGORY_CHOICES,
        'today': today,
    }
    return render(request, 'tasks/list.html', context)


@login_required
def task_create_view(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect('tasks:list')
        else:
            # Inline error formatting
            for field, errs in form.errors.items():
                for err in errs:
                    messages.error(request, f"{field.capitalize()}: {err}")
    else:
        form = TaskForm()

    return render(request, 'tasks/form.html', {'form': form, 'title': 'Create Task'})


@login_required
@require_POST
def quick_create_ajax(request):
    """AJAX endpoint for 10-second fast task creation."""
    try:
        data = json.loads(request.body.decode('utf-8'))
        title = data.get('title', '').strip()
        if not title:
            return JsonResponse({'success': False, 'error': 'Please enter a task title.'}, status=400)

        # Parse natural language if present
        parsed = parse_natural_language_task(title)
        
        # Priority override or suggested
        priority = data.get('priority') or parsed.get('priority', 'MEDIUM')
        category = data.get('category') or parsed.get('category', 'Work')
        due_date_str = data.get('due_date') or parsed.get('due_date')
        due_time_str = data.get('due_time') or parsed.get('due_time')

        due_date = datetime.date.fromisoformat(due_date_str) if due_date_str else datetime.date.today()
        due_time = None
        if due_time_str:
            try:
                due_time = datetime.time.fromisoformat(due_time_str)
            except ValueError:
                pass

        task = Task.objects.create(
            user=request.user,
            title=parsed.get('title') if not data.get('title_exact') else title,
            priority=priority,
            category=category,
            due_date=due_date,
            due_time=due_time,
            recurrence=parsed.get('recurrence', 'NONE'),
            status='PENDING'
        )

        return JsonResponse({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'priority': task.priority,
                'category': task.category,
                'due_date': str(task.due_date),
                'due_time': task.due_time.strftime('%H:%M') if task.due_time else '',
                'status': task.status,
                'time_tracking': task.time_to_complete_formatted,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def task_edit_view(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            updated = form.save()
            messages.success(request, f'Task "{updated.title}" updated!')
            return redirect('tasks:list')
    else:
        form = TaskForm(instance=task)

    return render(request, 'tasks/form.html', {'form': form, 'task': task, 'title': 'Edit Task'})


@login_required
@require_POST
def task_delete_view(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    title = task.title
    task.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': f'Task "{title}" deleted.'})
    messages.info(request, f'Task "{title}" has been deleted.')
    return redirect('tasks:list')


@login_required
@require_POST
def task_toggle_status_ajax(request, pk):
    """
    Single-tap status toggle endpoint.
    Cycles or toggles between PENDING -> IN_PROGRESS -> COMPLETED
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)
    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else {}
        target_status = data.get('status')
    except Exception:
        target_status = None

    if target_status:
        if target_status == 'COMPLETED':
            task.mark_completed()
        elif target_status == 'IN_PROGRESS':
            task.mark_in_progress()
        else:
            task.mark_pending()
    else:
        # Default toggle: If completed -> pending; if pending/overdue -> completed
        if task.status == 'COMPLETED':
            task.mark_pending()
        else:
            task.mark_completed()

    # Recalculate user task counts for live header badges
    user_tasks = Task.objects.filter(user=request.user)
    counts = {
        'total': user_tasks.count(),
        'pending': user_tasks.filter(status='PENDING').count(),
        'in_progress': user_tasks.filter(status='IN_PROGRESS').count(),
        'completed': user_tasks.filter(status='COMPLETED').count(),
        'overdue': user_tasks.filter(status='OVERDUE').count(),
    }

    return JsonResponse({
        'success': True,
        'id': task.id,
        'new_status': task.status,
        'status_display': task.get_status_display(),
        'is_completed': task.status == 'COMPLETED',
        'time_tracking': task.time_to_complete_formatted,
        'counts': counts
    })


@login_required
@require_GET
def task_parse_nl_ajax(request):
    """Natural-language text parsing helper."""
    text = request.GET.get('text', '')
    parsed = parse_natural_language_task(text)
    suggested_prio = suggest_priority(parsed.get('due_date'), parsed.get('due_time'))
    parsed['suggested_priority'] = suggested_prio
    return JsonResponse(parsed)

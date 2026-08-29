from django import forms
from django.utils import timezone
import datetime
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'description', 'category', 'priority', 'due_date', 'due_time', 'recurrence', 'status')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'What needs to get done?',
                'autofocus': 'autofocus',
                'id': 'task-title-input'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Add notes, checklist or details (optional)...',
                'rows': 3,
                'id': 'task-desc-input'
            }),
            'category': forms.Select(attrs={'class': 'form-select', 'id': 'task-category-input'}),
            'priority': forms.Select(attrs={'class': 'form-select', 'id': 'task-priority-input'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'task-date-input'}),
            'due_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'id': 'task-time-input'}),
            'recurrence': forms.Select(attrs={'class': 'form-select', 'id': 'task-recurrence-input'}),
            'status': forms.Select(attrs={'class': 'form-select', 'id': 'task-status-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate() if timezone.is_aware(timezone.now()) else datetime.date.today()
        if not self.instance.pk and not self.initial.get('due_date'):
            self.initial['due_date'] = today

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError("Please provide a task name so you know what to work on.")
        if len(title) < 2:
            raise forms.ValidationError("Task title is a bit too short. Please add at least 2 characters.")
        return title

    def clean(self):
        cleaned_data = super().clean()
        due_date = cleaned_data.get('due_date')
        due_time = cleaned_data.get('due_time')
        
        # When creating a new task, validate against past due dates/times
        if not self.instance.pk and due_date:
            today = timezone.localdate() if timezone.is_aware(timezone.now()) else datetime.date.today()
            if due_date < today:
                self.add_error('due_date', "Please pick today or a future due date for new tasks.")
            elif due_date == today and due_time:
                now_time = datetime.datetime.now().time()
                # allow 2-min grace for fast inputs
                grace_now = (datetime.datetime.now() - datetime.timedelta(minutes=2)).time()
                if due_time < grace_now:
                    self.add_error('due_time', "The time you picked has already passed. Please choose a future time today.")

        return cleaned_data


class QuickTaskForm(forms.ModelForm):
    """Ultra-streamlined task form for 10-second fast task creation."""
    class Meta:
        model = Task
        fields = ('title', 'priority', 'category', 'due_date', 'due_time')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Add a new task (e.g. "Prepare presentation tomorrow 4pm #Work high priority")...',
                'autofocus': 'autofocus',
                'id': 'quick-task-title'
            }),
            'priority': forms.Select(attrs={'class': 'form-select form-select-sm', 'id': 'quick-task-priority'}),
            'category': forms.Select(attrs={'class': 'form-select form-select-sm', 'id': 'quick-task-category'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date', 'id': 'quick-task-date'}),
            'due_time': forms.TimeInput(attrs={'class': 'form-control form-control-sm', 'type': 'time', 'id': 'quick-task-time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate() if timezone.is_aware(timezone.now()) else datetime.date.today()
        self.initial['due_date'] = today
        self.initial['priority'] = 'MEDIUM'
        self.initial['category'] = 'Work'

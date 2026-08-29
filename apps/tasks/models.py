from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('OVERDUE', 'Overdue'),
    ]

    CATEGORY_CHOICES = [
        ('Work', 'Work'),
        ('Personal', 'Personal'),
        ('Health', 'Health'),
        ('Study', 'Study'),
        ('Finance', 'Finance'),
        ('Other', 'Other'),
    ]

    RECURRENCE_CHOICES = [
        ('NONE', 'None'),
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255, help_text="Task title")
    description = models.TextField(blank=True, default="", help_text="Detailed description (optional)")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Work')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    
    # Due Date & Time
    due_date = models.DateField(default=timezone.now, help_text="Due date (defaults to today)")
    due_time = models.TimeField(null=True, blank=True, help_text="Due time (optional)")
    
    # Status & Progress
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Recurrence
    recurrence = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, default='NONE')
    
    # Time Tracking Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'due_date', 'due_time', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'due_date']),
            models.Index(fields=['user', 'priority']),
        ]

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"

    def get_due_datetime(self):
        """Returns due date combined with due time as a timezone-aware datetime."""
        if not self.due_date:
            return None
        t = self.due_time if self.due_time else datetime.time(23, 59, 59)
        combined = datetime.datetime.combine(self.due_date, t)
        if timezone.is_aware(timezone.now()):
            return timezone.make_aware(combined, timezone.get_current_timezone())
        return combined

    @property
    def is_overdue(self):
        """True if the task is not completed and past its due date/time."""
        if self.status == 'COMPLETED':
            return False
        due_dt = self.get_due_datetime()
        if not due_dt:
            return False
        now = timezone.now() if timezone.is_aware(due_dt) else datetime.datetime.now()
        return due_dt < now

    def update_dynamic_status(self):
        """Updates status to OVERDUE if deadline passed and not completed."""
        if self.status != 'COMPLETED' and self.is_overdue:
            if self.status != 'OVERDUE':
                self.status = 'OVERDUE'
                self.save(update_fields=['status'])
        elif self.status == 'OVERDUE' and not self.is_overdue:
            self.status = 'PENDING'
            self.save(update_fields=['status'])

    def mark_completed(self):
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])

    def mark_in_progress(self):
        self.status = 'IN_PROGRESS'
        if not self.started_at:
            self.started_at = timezone.now()
        self.completed_at = None
        self.save(update_fields=['status', 'started_at', 'completed_at', 'updated_at'])

    def mark_pending(self):
        self.status = 'PENDING'
        self.completed_at = None
        self.save(update_fields=['status', 'completed_at', 'updated_at'])

    @property
    def duration_seconds(self):
        """Total seconds taken to complete, or running elapsed duration."""
        if self.completed_at:
            start = self.started_at or self.created_at
            return max(0, int((self.completed_at - start).total_seconds()))
        else:
            start = self.started_at or self.created_at
            now = timezone.now()
            return max(0, int((now - start).total_seconds()))

    @property
    def time_to_complete_formatted(self):
        """Returns 'Completed in 2h 15m' or 'In progress for 45m'."""
        secs = self.duration_seconds
        days = secs // 86400
        hours = (secs % 86400) // 3600
        minutes = (secs % 3600) // 60

        if days > 0:
            formatted = f"{days}d {hours}h"
        elif hours > 0:
            formatted = f"{hours}h {minutes}m"
        else:
            formatted = f"{max(1, minutes)}m"

        if self.status == 'COMPLETED':
            return f"Completed in {formatted}"
        elif self.status == 'IN_PROGRESS':
            return f"In progress for {formatted}"
        else:
            return f"Created {formatted} ago"

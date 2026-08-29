from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ReminderLog(models.Model):
    REMINDER_TYPES = [
        ('TASK', 'Task Deadline'),
        ('MEDICINE', 'Medication Dose'),
        ('HYDRATION', 'Hydration Nudge'),
        ('WELLNESS', 'Wellness Break'),
    ]

    STAGES = [
        ('GENTLE', 'Gentle Reminder'),
        ('URGENT', 'Urgent Alert'),
        ('OVERDUE', 'Overdue Notice'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending Delivery'),
        ('DELIVERED', 'Delivered'),
        ('DISMISSED', 'Dismissed'),
        ('SNOOZED', 'Snoozed'),
        ('ACTIONED', 'Actioned / Done'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminder_logs')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES)
    reference_id = models.PositiveIntegerField(null=True, blank=True, help_text="Task ID or Medicine ID")
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    stage = models.CharField(max_length=20, choices=STAGES, default='GENTLE')
    
    scheduled_for = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    snooze_until = models.DateTimeField(null=True, blank=True)
    
    is_alarm_urgent = models.BooleanField(default=False, help_text="Triggers audible chime / loud alert in browser")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['reminder_type', 'reference_id']),
        ]

    def __str__(self):
        return f"[{self.get_reminder_type_display()} - {self.get_stage_display()}] {self.title} for {self.user.username}"

    def mark_delivered(self):
        self.status = 'DELIVERED'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at'])

    def mark_dismissed(self):
        self.status = 'DISMISSED'
        self.save(update_fields=['status'])

    def snooze(self, minutes=15):
        self.status = 'SNOOZED'
        self.snooze_until = timezone.now() + timezone.timedelta(minutes=minutes)
        self.save(update_fields=['status', 'snooze_until'])

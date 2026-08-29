from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

class WellnessTip(models.Model):
    CATEGORY_CHOICES = [
        ('HYDRATION', 'Hydration'),
        ('POSTURE', 'Posture & Ergonomics'),
        ('EYES', 'Eye Health (20-20-20)'),
        ('MOVEMENT', 'Movement & Stretch'),
        ('BREATH', 'Mindfulness & Breathing'),
    ]

    title = models.CharField(max_length=120)
    tip_text = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='HYDRATION')
    action_label = models.CharField(max_length=50, default='Got it!')
    icon = models.CharField(max_length=50, default='bi-droplet', help_text='Bootstrap Icon class')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"


class Medicine(models.Model):
    FREQUENCY_CHOICES = [
        ('ONCE', 'Once daily'),
        ('TWICE', 'Twice daily'),
        ('THRICE', 'Thrice daily'),
        ('CUSTOM', 'Custom times'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medicines')
    name = models.CharField(max_length=200, help_text="e.g. Vitamin D3, Metformin, Amoxicillin")
    dosage = models.CharField(max_length=100, help_text="e.g. 500mg, 1 tablet, 10ml")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='ONCE')
    
    # Store list of time strings like ["08:00", "20:00"]
    scheduled_times = models.JSONField(default=list, help_text="List of scheduled times in HH:MM format")
    
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True, help_text="Leave blank if ongoing")
    notes = models.CharField(max_length=255, blank=True, default="", help_text="e.g. After meals, with full glass of water")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.dosage}) - {self.get_frequency_display()}"

    def get_times_display(self):
        if not self.scheduled_times:
            return "No times set"
        return ", ".join(self.scheduled_times)

    def is_currently_active(self):
        today = timezone.localdate() if timezone.is_aware(timezone.now()) else datetime.date.today()
        if not self.is_active:
            return False
        if self.start_date and self.start_date > today:
            return False
        if self.end_date and self.end_date < today:
            return False
        return True


class MedicineLog(models.Model):
    STATUS_CHOICES = [
        ('TAKEN', 'Taken'),
        ('SKIPPED', 'Skipped'),
        ('SNOOZED', 'Snoozed'),
    ]

    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medicine_logs')
    scheduled_date = models.DateField(default=timezone.now)
    scheduled_time = models.CharField(max_length=10, help_text="HH:MM string of scheduled dose")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='TAKEN')
    logged_at = models.DateTimeField(auto_now_add=True)
    notes = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        ordering = ['-scheduled_date', '-logged_at']
        unique_together = ('medicine', 'scheduled_date', 'scheduled_time')

    def __str__(self):
        return f"{self.medicine.name} at {self.scheduled_time} on {self.scheduled_date}: {self.status}"


class HydrationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hydration_logs')
    logged_at = models.DateTimeField(default=timezone.now)
    glasses = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['-logged_at']

    def __str__(self):
        return f"{self.user.username} drank {self.glasses} glass(es) at {self.logged_at}"

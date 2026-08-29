from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other / Prefer not to say'),
    ]

    ACTIVITY_CHOICES = [
        ('SEDENTARY', 'Sedentary / Desk Work (Busy Office/Coding)'),
        ('MODERATE', 'Moderate (Light Exercise / Walking)'),
        ('HIGH', 'High Activity (Heavy Physical Work / Sports)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Demographic & WHO Health Metrics
    age = models.PositiveIntegerField(default=28, help_text="Age in years (used for WHO hydration & health guidelines)")
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, default='M')
    weight_kg = models.FloatField(default=68.0, help_text="Weight in kilograms")
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_CHOICES, default='SEDENTARY')
    
    # Active working hours
    active_hours_start = models.TimeField(default=datetime.time(9, 0), help_text="Start of active work hours (e.g. 09:00)")
    active_hours_end = models.TimeField(default=datetime.time(18, 0), help_text="End of active work hours (e.g. 18:00)")
    
    # Hydration & Wellness Settings (Calculated via WHO guidelines or custom)
    hydration_interval_minutes = models.PositiveIntegerField(default=60, help_text="Interval between water nudges in minutes")
    water_daily_target = models.PositiveIntegerField(default=10, help_text="Daily water goal in glasses (250ml per glass)")
    water_intake_today = models.PositiveIntegerField(default=0, help_text="Glasses of water logged today")
    last_water_logged_at = models.DateTimeField(null=True, blank=True)
    last_hydration_nudge_at = models.DateTimeField(null=True, blank=True)
    last_water_reset_date = models.DateField(default=timezone.now)
    last_tip_index = models.PositiveIntegerField(default=0)
    
    # Reminder Settings (Gentle advance window default 30 min, 5-min urgent alarm automatic)
    reminder_window_minutes = models.PositiveIntegerField(default=30, help_text="Minutes before task deadline to send gentle advance notice (Urgent alarm fires automatically at 5 minutes)")
    sound_alerts_enabled = models.BooleanField(default=True, help_text="Play audible alarm chimes for tasks and health/medications")
    
    # Web Push Notification Subscription (JSON)
    push_subscription = models.JSONField(null=True, blank=True, help_text="Browser Web Push subscription payload")
    
    # Onboarding status
    onboarding_completed = models.BooleanField(default=False, help_text="Whether user has completed the 3-step walkthrough")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_who_recommended_water_glasses(self):
        """
        Calculates WHO (World Health Organization) and EFSA recommended daily water intake
        based on user Age, Gender, Weight, and busy desk activity level.
        Returns: (recommended_glasses, recommended_liters, explanation_str)
        """
        base_ml = self.weight_kg * 35.0

        # Age adjustments (WHO Guidelines)
        if self.age < 18:
            base_ml = max(1800, self.weight_kg * 38.0)
        elif 18 <= self.age <= 50:
            if self.gender == 'M':
                base_ml = max(2800, self.weight_kg * 35.0) # ~3.0L for men
            elif self.gender == 'F':
                base_ml = max(2200, self.weight_kg * 33.0) # ~2.5L for women
            else:
                base_ml = max(2500, self.weight_kg * 34.0)
        elif 51 <= self.age <= 65:
            base_ml = max(2200, self.weight_kg * 32.0)
        else:
            base_ml = max(2000, self.weight_kg * 30.0)

        # Activity level adjustment
        if self.activity_level == 'MODERATE':
            base_ml += 400
        elif self.activity_level == 'HIGH':
            base_ml += 800

        liters = round(base_ml / 1000.0, 1)
        glasses = max(6, min(16, round(base_ml / 250.0)))
        explanation = f"WHO guideline for Age {self.age} ({self.get_gender_display()}): ~{liters}L ({glasses} glasses/day)"
        return glasses, liters, explanation

    def calculate_adaptive_hydration_interval_minutes(self):
        """
        Calculates optimal minutes between glasses during active work hours.
        e.g., if working 9 hours (540 mins) and goal is 9 glasses -> 60 minutes.
        """
        start_m = self.active_hours_start.hour * 60 + self.active_hours_start.minute
        end_m = self.active_hours_end.hour * 60 + self.active_hours_end.minute
        
        if end_m > start_m:
            total_active_mins = end_m - start_m
        else:
            total_active_mins = (24 * 60 - start_m) + end_m
            
        target_glasses = max(1, self.water_daily_target)
        interval = max(30, int(total_active_mins / target_glasses))
        return interval

    def apply_who_guidelines(self):
        glasses, _, _ = self.calculate_who_recommended_water_glasses()
        self.water_daily_target = glasses
        self.hydration_interval_minutes = self.calculate_adaptive_hydration_interval_minutes()

    def __str__(self):
        return f"Profile of {self.user.username} (Age: {self.age}, Water Goal: {self.water_daily_target} glasses)"

    def check_and_reset_daily_water(self):
        """Resets today's water count if a new day has started."""
        today = timezone.localdate() if timezone.is_aware(timezone.now()) else datetime.date.today()
        if self.last_water_reset_date != today:
            self.water_intake_today = 0
            self.last_water_reset_date = today
            self.save(update_fields=['water_intake_today', 'last_water_reset_date'])

    def is_within_active_hours(self, current_time=None):
        """Check if the provided or current time falls within user active work hours."""
        if not current_time:
            current_time = datetime.datetime.now().time()
        
        if self.active_hours_start <= self.active_hours_end:
            return self.active_hours_start <= current_time <= self.active_hours_end
        else:
            # Over-midnight shift
            return current_time >= self.active_hours_start or current_time <= self.active_hours_end

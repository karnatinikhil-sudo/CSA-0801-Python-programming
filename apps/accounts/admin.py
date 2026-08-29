from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'active_hours_start', 'active_hours_end', 'water_intake_today', 'onboarding_completed')
    search_fields = ('user__username', 'user__email')

from django.contrib import admin
from .models import ReminderLog

@admin.register(ReminderLog)
class ReminderLogAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'reminder_type', 'stage', 'status', 'is_alarm_urgent', 'created_at', 'sent_at')
    list_filter = ('reminder_type', 'stage', 'status', 'is_alarm_urgent')
    search_fields = ('title', 'message', 'user__username')

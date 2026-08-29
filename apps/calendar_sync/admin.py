from django.contrib import admin
from .models import CalendarConnection

@admin.register(CalendarConnection)
class CalendarConnectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_connected', 'last_synced_at', 'created_at')
    list_filter = ('is_connected',)

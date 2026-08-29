from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'priority', 'category', 'due_date', 'due_time', 'status', 'created_at', 'completed_at')
    list_filter = ('status', 'priority', 'category', 'due_date')
    search_fields = ('title', 'description', 'user__username')

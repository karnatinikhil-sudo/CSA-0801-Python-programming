from django.db import models
from django.contrib.auth.models import User

class CalendarConnection(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='calendar_connection')
    is_connected = models.BooleanField(default=False)
    google_credentials_json = models.TextField(blank=True, default="", help_text="Stored OAuth credentials token")
    google_calendar_id = models.CharField(max_length=255, default="primary")
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        status = "Connected" if self.is_connected else "Disconnected"
        return f"Google Calendar for {self.user.username} [{status}]"

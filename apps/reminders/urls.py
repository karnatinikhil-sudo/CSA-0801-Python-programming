from django.urls import path
from . import views

app_name = 'reminders'

urlpatterns = [
    path('active/', views.get_active_notifications_ajax, name='get_active'),
    path('<int:pk>/dismiss/', views.dismiss_notification_ajax, name='dismiss'),
    path('<int:pk>/snooze/', views.snooze_notification_ajax, name='snooze'),
    path('test-trigger/', views.trigger_test_reminder_ajax, name='test_trigger'),
]

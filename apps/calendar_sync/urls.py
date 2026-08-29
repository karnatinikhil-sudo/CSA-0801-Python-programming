from django.urls import path
from . import views

app_name = 'calendar_sync'

urlpatterns = [
    path('settings/', views.calendar_settings_view, name='settings'),
    path('task/<int:pk>/ics/', views.export_task_ics_view, name='export_task_ics'),
    path('export/all-tasks.ics', views.export_all_tasks_ics_view, name='export_all_tasks_ics'),
    path('export/medications.ics', views.export_medication_ics_view, name='export_medication_ics'),
    path('connect/', views.google_oauth_start, name='google_connect'),
    path('oauth2callback/', views.google_oauth_callback, name='google_callback'),
    path('disconnect/', views.disconnect_google_calendar, name='google_disconnect'),
    path('check-conflict/', views.check_conflict_ajax, name='check_conflict'),
]

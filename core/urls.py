from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.dashboard import views as dashboard_views

urlpatterns = [
    path('manifest.json', dashboard_views.manifest_view, name='pwa_manifest'),
    path('sw.js', dashboard_views.service_worker_view, name='pwa_service_worker'),
    path('offline/', dashboard_views.offline_view, name='pwa_offline'),
    path('admin/', admin.site.urls),
    path('auth/', include('apps.accounts.urls', namespace='accounts')),
    path('', include('apps.dashboard.urls', namespace='dashboard')),
    path('tasks/', include('apps.tasks.urls', namespace='tasks')),
    path('health/', include('apps.health.urls', namespace='health')),
    path('reminders/', include('apps.reminders.urls', namespace='reminders')),
    path('calendar/', include('apps.calendar_sync.urls', namespace='calendar_sync')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


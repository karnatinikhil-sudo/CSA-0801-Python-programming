from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list_view, name='list'),
    path('new/', views.task_create_view, name='create'),
    path('quick-create/', views.quick_create_ajax, name='quick_create'),
    path('<int:pk>/edit/', views.task_edit_view, name='edit'),
    path('<int:pk>/delete/', views.task_delete_view, name='delete'),
    path('<int:pk>/toggle/', views.task_toggle_status_ajax, name='toggle_status'),
    path('parse-nl/', views.task_parse_nl_ajax, name='parse_nl'),
]

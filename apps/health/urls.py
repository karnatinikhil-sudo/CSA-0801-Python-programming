from django.urls import path
from . import views

app_name = 'health'

urlpatterns = [
    path('medicines/', views.medicine_list_view, name='medicines'),
    path('medicines/new/', views.medicine_create_view, name='medicine_create'),
    path('medicines/<int:pk>/edit/', views.medicine_edit_view, name='medicine_edit'),
    path('medicines/<int:pk>/delete/', views.medicine_delete_view, name='medicine_delete'),
    path('water/log/', views.log_water_intake_ajax, name='log_water'),
    path('tips/next/', views.next_wellness_tip_ajax, name='next_tip'),
    path('medicines/log-action/', views.log_medicine_action_ajax, name='log_medicine_action'),
]

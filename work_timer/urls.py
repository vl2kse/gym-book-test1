from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.timer_status, name='timer_status'),
    path('start/', views.timer_start, name='timer_start'),
    path('stop/', views.timer_stop, name='timer_stop'),
    path('settings/', views.timer_settings_get, name='timer_settings_get'),
    path('settings/save/', views.timer_settings_save, name='timer_settings_save'),
    path('history/', views.timer_history, name='timer_history'),
    path('session/<int:pk>/edit/', views.session_edit, name='session_edit'),
    path('session/<int:pk>/delete/', views.session_delete, name='session_delete'),
]

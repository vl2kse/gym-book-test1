from django.contrib import admin
from .models import WorkSession, TimerSettings


@admin.register(WorkSession)
class WorkSessionAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time', 'is_running_display')
    list_filter = ('start_time',)
    readonly_fields = ('start_time', 'end_time')

    def is_running_display(self, obj):
        return 'Активна' if obj.is_running else 'Завершена'
    is_running_display.short_description = 'Статус'


@admin.register(TimerSettings)
class TimerSettingsAdmin(admin.ModelAdmin):
    list_display = ('daily_goal_hours',)

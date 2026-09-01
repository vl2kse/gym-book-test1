from django.db import models


class WorkSession(models.Model):
    """Одиночный интервал работы (старт-стоп)."""
    start_time = models.DateTimeField(
        verbose_name='Начало',
        auto_now_add=True,
    )
    end_time = models.DateTimeField(
        verbose_name='Конец',
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['-start_time']
        verbose_name = 'Сессия работы'
        verbose_name_plural = 'Сессии работы'

    @property
    def duration_seconds(self):
        end = self.end_time
        if end is None:
            from django.utils.timezone import now
            end = now()
        return (end - self.start_time).total_seconds()

    @property
    def is_running(self):
        return self.end_time is None


class TimerSettings(models.Model):
    """Настройки таймера (одна запись-синглтон)."""
    daily_goal_hours = models.FloatField(
        verbose_name='Цель на день (часы)',
        default=8.0,
    )

    class Meta:
        verbose_name = 'Настройки таймера'
        verbose_name_plural = 'Настройки таймера'

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

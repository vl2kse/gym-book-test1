import json
from django.http import JsonResponse
from django.utils.timezone import now, localtime
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.db import transaction
from datetime import timedelta, date

from .models import WorkSession, TimerSettings


# ---------- helpers ----------

def _today_sessions():
    """Все сессии за сегодняшний день (по серверному времени)."""
    tz_now = localtime(now())
    today = tz_now.date()
    return WorkSession.objects.filter(
        start_time__date=today,
    )


def _today_total_seconds():
    """Сумма завершённых + текущая незавершённая (если есть)."""
    total = 0
    for s in _today_sessions():
        total += s.duration_seconds
    return total


def _running_session():
    """Текущая незавершённая сессия или None."""
    return WorkSession.objects.filter(end_time__isnull=True).first()


def _status_payload():
    running = _running_session()
    total = _today_total_seconds()
    settings = TimerSettings.get_settings()
    goal_seconds = settings.daily_goal_hours * 3600
    payload = {
        'is_running': running is not None,
        'elapsed': running.duration_seconds if running else 0,
        'today_total': total,
        'today_goal': goal_seconds,
        'session_start': running.start_time.isoformat() if running else None,
    }
    return payload


# ---------- views ----------

@require_GET
@ensure_csrf_cookie
def timer_status(request):
    """Текущее состояние таймера и суммарное время за сегодня."""
    return JsonResponse(_status_payload())


@require_POST
@csrf_exempt
def timer_start(request):
    """Начать новую сессию. Если уже есть активная — ничего не делаем."""
    if _running_session() is not None:
        return JsonResponse({'error': 'Таймер уже запущен'}, status=409)

    WorkSession.objects.create()
    return JsonResponse(_status_payload())


@require_POST
@csrf_exempt
def timer_stop(request):
    """Остановить текущую сессию."""
    session = _running_session()
    if session is None:
        return JsonResponse({'error': 'Нет активной сессии'}, status=409)

    session.end_time = now()
    session.save(update_fields=['end_time'])
    return JsonResponse(_status_payload())


@require_GET
def timer_settings_get(request):
    """Получить настройки."""
    s = TimerSettings.get_settings()
    return JsonResponse({'daily_goal_hours': s.daily_goal_hours})


@require_POST
@csrf_exempt
def timer_settings_save(request):
    """Сохранить настройки."""
    data = json.loads(request.body)
    s = TimerSettings.get_settings()
    hours = data.get('daily_goal_hours')
    if hours is not None:
        try:
            s.daily_goal_hours = float(hours)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Неверное значение'}, status=400)
    s.save()
    return JsonResponse({'daily_goal_hours': s.daily_goal_hours})


@require_GET
def timer_history(request):
    """История сессий за последние 7 дней (для виджета / отдельной страницы)."""
    tz_now = localtime(now())
    cutoff = tz_now - timedelta(days=7)
    sessions = WorkSession.objects.filter(
        start_time__gte=cutoff,
    ).order_by('-start_time')
    data = []
    for s in sessions:
        lt = localtime(s.start_time)
        end_str = localtime(s.end_time).strftime('%H:%M') if s.end_time else None
        data.append({
            'date': lt.strftime('%d.%m'),
            'start': lt.strftime('%H:%M'),
            'end': end_str,
            'duration': round(s.duration_seconds, 1),
            'is_running': s.is_running,
        })
    return JsonResponse({'sessions': data})

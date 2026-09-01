from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
import json
from collections import OrderedDict
from datetime import timedelta

from django.db import models
from .models import Exercise, Set, BodyWeight


# ============================================================
# Dashboard
# ============================================================

def dashboard(request):
    total_sets = Set.objects.count()
    exercises = Exercise.objects.all()

    today = timezone.now().date()
    today_sets = Set.objects.filter(date=today).select_related("exercise")
    today_total = sum(s.reps for s in today_sets)

    # Разделяем упражнения: с весом и без
    bw_exercises = []  # bodyweight (вес = 0)
    wt_exercises = []  # weighted (вес > 0)
    for ex in exercises:
        has_weight = Set.objects.filter(exercise=ex, weight__gt=0).exists()
        if has_weight:
            wt_exercises.append(ex)
        else:
            bw_exercises.append(ex)

    # Все даты
    all_dates_bw = Set.objects.filter(exercise__in=bw_exercises).dates('date', 'day', order='ASC') if bw_exercises else []
    all_dates_wt = Set.objects.filter(exercise__in=wt_exercises).dates('date', 'day', order='ASC') if wt_exercises else []

    bw_date_labels = [d.isoformat() for d in all_dates_bw]
    wt_date_labels = [d.isoformat() for d in all_dates_wt]

    colors = ['#667eea', '#764ba2', '#e74c3c', '#2ecc71', '#f39c12', '#1abc9c', '#e67e22', '#3498db']

    # Чарт 1: без веса — сумма повторений по дням
    bw_datasets = []
    for i, ex in enumerate(bw_exercises):
        daily = OrderedDict()
        for d in all_dates_bw:
            daily[d] = 0
        sets_ex = Set.objects.filter(exercise=ex).values('date').annotate(total=models.Sum('reps'))
        for s in sets_ex:
            if s['date'] in daily:
                daily[s['date']] = s['total'] or 0
        bw_datasets.append({
            'label': ex.display_name,
            'data': list(daily.values()),
            'borderColor': colors[i % len(colors)],
            'backgroundColor': colors[i % len(colors)] + '20',
            'fill': False, 'tension': 0.3, 'pointRadius': 4,
        })

    # Чарт 2: с весом — сумма (повторения * вес) по дням = общая поднятая масса
    wt_datasets = []
    for i, ex in enumerate(wt_exercises):
        daily = OrderedDict()
        for d in all_dates_wt:
            daily[d] = 0
        sets_ex = Set.objects.filter(exercise=ex, weight__gt=0).values('date').annotate(
            total_mass=models.Sum(models.F('reps') * models.F('weight'))
        )
        for s in sets_ex:
            if s['date'] in daily:
                daily[s['date']] = float(s['total_mass'] or 0)
        wt_datasets.append({
            'label': ex.display_name,
            'data': list(daily.values()),
            'borderColor': colors[i % len(colors)],
            'backgroundColor': colors[i % len(colors)] + '20',
            'fill': False, 'tension': 0.3, 'pointRadius': 4,
        })

    context = {
        "total_sets": total_sets,
        "today_sets": today_sets,
        "today_total": today_total,
        "today": today,
        "exercises": exercises,
        "bw_date_labels": json.dumps(bw_date_labels),
        "bw_datasets": json.dumps(bw_datasets),
        "wt_date_labels": json.dumps(wt_date_labels),
        "wt_datasets": json.dumps(wt_datasets),
    }
    return render(request, "workouts/dashboard.html", context)


# ============================================================
# Быстрое добавление подхода (из дашборда)
# ============================================================

def set_quick_add(request):
    if request.method == "POST":
        exercise_id = request.POST.get("exercise_id")
        reps = request.POST.get("reps", "0")
        weight = request.POST.get("weight", "0")
        date_str = request.POST.get("date", "")

        if exercise_id and int(reps) > 0:
            from datetime import datetime
            set_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else timezone.now().date()
            Set.objects.create(
                date=set_date,
                exercise_id=exercise_id,
                reps=int(reps),
                weight=float(weight) or 0,
            )
        return redirect("dashboard")


# ============================================================
# Добавить подходы (полная страница из дашборда)
# ============================================================

def set_add(request):
    if request.method == "POST":
        date_str = request.POST.get("date", "")
        sets_data = request.POST.get("sets_data", "[]")

        from datetime import datetime
        set_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else timezone.now().date()

        sets = json.loads(sets_data)
        for s in sets:
            exercise_id = s.get("exercise_id")
            reps = s.get("reps", 0)
            weight = s.get("weight", 0)
            if exercise_id and reps > 0:
                Set.objects.create(
                    date=set_date,
                    exercise_id=exercise_id,
                    reps=reps,
                    weight=weight,
                )

        return redirect("dashboard")

    exercises = Exercise.objects.all()
    today = timezone.now().strftime("%Y-%m-%d")
    return render(request, "workouts/set_add.html", {"exercises": exercises, "today": today})


# ============================================================
# Удаление подхода
# ============================================================

def set_delete(request, pk):
    s = get_object_or_404(Set, pk=pk)
    if request.method == "POST":
        s.delete()
    return redirect("dashboard")


# ============================================================
# История (все подходы по датам)
# ============================================================

def set_history(request):
    sets = Set.objects.select_related("exercise").all()
    return render(request, "workouts/set_history.html", {"sets": sets})


# ============================================================
# Упражнения (справочник)
# ============================================================

def exercise_list(request):
    exercises = Exercise.objects.all()
    return render(request, "workouts/exercise_list.html", {"exercises": exercises})


def exercise_add(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        if name:
            Exercise.objects.create(name=name, description=description)
        return redirect("exercise_list")
    return render(request, "workouts/exercise_form.html")


def exercise_delete(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    if request.method == "POST":
        exercise.delete()
    return redirect("exercise_list")


# ============================================================
# Прогресс по упражнению
# ============================================================

def exercise_progress(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    sets = Set.objects.filter(exercise=exercise).order_by("date", "id")

    # Агрегация по дате
    daily = OrderedDict()
    for s in sets:
        d = s.date
        if d not in daily:
            daily[d] = {"total_reps": 0, "sets_count": 0, "max_weight": 0}
        daily[d]["total_reps"] += s.reps
        daily[d]["sets_count"] += 1
        w = float(s.weight)
        if w > daily[d]["max_weight"]:
            daily[d]["max_weight"] = w

    daily_dates = [d.isoformat() for d in daily.keys()]
    daily_reps = [v["total_reps"] for v in daily.values()]
    daily_sets = [v["sets_count"] for v in daily.values()]
    daily_max_weight = [v["max_weight"] for v in daily.values()]

    # Статистика
    all_reps = [s.reps for s in sets]
    stats = {}
    if all_reps:
        stats["max"] = max(all_reps)
        stats["min"] = min(all_reps)
        stats["avg"] = round(sum(all_reps) / len(all_reps), 1)
        stats["total"] = sum(all_reps)
        stats["days"] = len(daily)

    context = {
        "exercise": exercise,
        "stats": stats,
        "daily_dates": json.dumps(daily_dates),
        "daily_reps": json.dumps(daily_reps),
        "daily_sets": json.dumps(daily_sets),
        "daily_max_weight": json.dumps(daily_max_weight),
    }
    return render(request, "workouts/exercise_progress.html", context)


# ============================================================
# Вес тела
# ============================================================

def bodyweight_list(request):
    entries = BodyWeight.objects.order_by("-date").all()

    weight_data = BodyWeight.objects.order_by("date").all()
    dates = [w.date.isoformat() for w in weight_data]
    values = [float(w.weight) for w in weight_data]

    stats = {}
    if values:
        stats["max"] = max(values)
        stats["min"] = min(values)
        stats["avg"] = round(sum(values) / len(values), 1)
        stats["last"] = values[-1] if values else None
        stats["first"] = values[0] if values else None
        if len(values) >= 2:
            stats["change"] = round(values[-1] - values[0], 1)
        else:
            stats["change"] = 0

    context = {
        "entries": entries,
        "dates": json.dumps(dates),
        "values": json.dumps(values),
        "stats": stats,
    }
    return render(request, "workouts/bodyweight.html", context)


def bodyweight_add(request):
    if request.method == "POST":
        date_str = request.POST.get("date", "")
        weight = request.POST.get("weight", "")
        if date_str and weight:
            from datetime import datetime
            bw_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            BodyWeight.objects.update_or_create(
                date=bw_date,
                defaults={"weight": weight},
            )
        return redirect("bodyweight_list")
    today = timezone.now().strftime("%Y-%m-%d")
    return render(request, "workouts/bodyweight_form.html", {"today": today})


def bodyweight_delete(request, pk):
    entry = get_object_or_404(BodyWeight, pk=pk)
    if request.method == "POST":
        entry.delete()
    return redirect("bodyweight_list")

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

    # График: по горизонтали даты, по вертикали сумма повторений за день, по каждому упражнению
    all_dates = Set.objects.dates('date', 'day', order='ASC')
    date_labels = [d.isoformat() for d in all_dates]

    chart_datasets = []
    colors = ['#667eea', '#764ba2', '#e74c3c', '#2ecc71', '#f39c12', '#1abc9c', '#e67e22', '#3498db']

    for i, ex in enumerate(exercises):
        # Сумма повторений по дням
        daily = OrderedDict()
        for d in all_dates:
            daily[d] = 0
        sets_ex = Set.objects.filter(exercise=ex).values('date').annotate(total=models.Sum('reps'))
        for s in sets_ex:
            if s['date'] in daily:
                daily[s['date']] = s['total'] or 0

        chart_datasets.append({
            'label': ex.display_name,
            'data': list(daily.values()),
            'borderColor': colors[i % len(colors)],
            'backgroundColor': colors[i % len(colors)] + '20',
            'fill': False,
            'tension': 0.3,
            'pointRadius': 4,
        })

    # Вес тела (последние 14 записей)
    weight_entries = BodyWeight.objects.order_by("date")[:14]
    weight_dates = [w.date.isoformat() for w in weight_entries]
    weight_values = [float(w.weight) for w in weight_entries]

    context = {
        "total_sets": total_sets,
        "today_sets": today_sets,
        "today_total": today_total,
        "today": today,
        "exercises": exercises,
        "date_labels": json.dumps(date_labels),
        "chart_datasets": json.dumps(chart_datasets),
        "weight_dates": json.dumps(weight_dates),
        "weight_values": json.dumps(weight_values),
    }
    return render(request, "workouts/dashboard.html", context)


# ============================================================
# Добавить подходы
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

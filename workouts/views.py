from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

from .models import Exercise, Workout, Set, BodyWeight


# ============================================================
# Dashboard
# ============================================================

def dashboard(request):
    total_workouts = Workout.objects.count()
    total_sets = Set.objects.count()
    exercises = Exercise.objects.all()

    last_workout = Workout.objects.first()
    last_sets = []
    if last_workout:
        last_sets = last_workout.sets.select_related("exercise").all()

    # Статистика по каждому упражнению (последние 7 записей)
    exercise_stats = []
    for ex in exercises:
        sets = Set.objects.filter(exercise=ex).order_by("-workout__date")[:7]
        if sets.exists():
            dates = [s.workout.date.isoformat() for s in reversed(sets)]
            reps = [s.reps for s in reversed(sets)]
            exercise_stats.append({"exercise": ex, "dates": dates, "reps": reps})

    # Вес тела (последние 14 записей)
    weight_entries = BodyWeight.objects.order_by("date")[:14]
    weight_dates = [w.date.isoformat() for w in weight_entries]
    weight_values = [float(w.weight) for w in weight_entries]

    context = {
        "total_workouts": total_workouts,
        "total_sets": total_sets,
        "last_workout": last_workout,
        "last_sets": last_sets,
        "exercise_stats": exercise_stats,
        "weight_dates": json.dumps(weight_dates),
        "weight_values": json.dumps(weight_values),
    }
    return render(request, "workouts/dashboard.html", context)


# ============================================================
# Новая тренировка
# ============================================================

def workout_new(request):
    if request.method == "POST":
        date_str = request.POST.get("date", "")
        notes = request.POST.get("notes", "")
        sets_data = request.POST.get("sets_data", "[]")

        from datetime import datetime
        workout_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else timezone.now().date()

        workout = Workout.objects.create(date=workout_date, notes=notes)

        sets = json.loads(sets_data)
        for s in sets:
            exercise_id = s.get("exercise_id")
            reps = s.get("reps", 0)
            weight = s.get("weight", 0)
            if exercise_id and reps > 0:
                Set.objects.create(
                    workout=workout,
                    exercise_id=exercise_id,
                    reps=reps,
                    weight=weight,
                )

        return redirect("dashboard")

    exercises = Exercise.objects.all()
    today = timezone.now().strftime("%Y-%m-%d")
    return render(request, "workouts/workout_new.html", {"exercises": exercises, "today": today})


# ============================================================
# История тренировок
# ============================================================

def workout_history(request):
    workouts = Workout.objects.prefetch_related("sets__exercise").all()
    return render(request, "workouts/workout_history.html", {"workouts": workouts})


# ============================================================
# Удаление тренировки
# ============================================================

def workout_delete(request, pk):
    workout = get_object_or_404(Workout, pk=pk)
    if request.method == "POST":
        workout.delete()
    return redirect("workout_history")


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
    sets = Set.objects.filter(exercise=exercise).select_related("workout").order_by("workout__date", "id")

    dates = []
    reps_list = []
    weights = []
    seen_dates = set()

    for s in sets:
        d = s.workout.date.isoformat()
        dates.append(d)
        reps_list.append(s.reps)
        weights.append(float(s.weight))
        seen_dates.add(d)

    # Агрегация по дате (сумма повторений за тренировку)
    from collections import OrderedDict
    daily = OrderedDict()
    for s in sets:
        d = s.workout.date
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
        stats["workouts"] = len(seen_dates)

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

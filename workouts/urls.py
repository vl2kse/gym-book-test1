from django.urls import path
from . import views

app_name = "workouts"

urlpatterns = [
    # Дашборд
    path("", views.dashboard, name="dashboard"),

    # Тренировки
    path("workout/new/", views.workout_new, name="workout_new"),
    path("workout/history/", views.workout_history, name="workout_history"),
    path("workout/<int:pk>/delete/", views.workout_delete, name="workout_delete"),

    # Упражнения
    path("exercises/", views.exercise_list, name="exercise_list"),
    path("exercises/add/", views.exercise_add, name="exercise_add"),
    path("exercises/<int:pk>/delete/", views.exercise_delete, name="exercise_delete"),

    # Прогресс
    path("exercises/<int:pk>/progress/", views.exercise_progress, name="exercise_progress"),

    # Вес тела
    path("bodyweight/", views.bodyweight_list, name="bodyweight_list"),
    path("bodyweight/add/", views.bodyweight_add, name="bodyweight_add"),
    path("bodyweight/<int:pk>/delete/", views.bodyweight_delete, name="bodyweight_delete"),
]

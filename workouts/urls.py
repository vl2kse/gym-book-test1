from django.urls import path
from . import views

urlpatterns = [
    # Дашборд
    path("", views.dashboard, name="dashboard"),

    # Подходы
    path("set/add/", views.set_add, name="set_add"),
    path("set/<int:pk>/delete/", views.set_delete, name="set_delete"),
    path("set/history/", views.set_history, name="set_history"),

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

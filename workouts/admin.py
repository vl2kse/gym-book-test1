from django.contrib import admin
from .models import Exercise, Workout, Set, BodyWeight


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ("date", "notes")
    list_filter = ("date",)
    date_hierarchy = "date"


@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ("workout", "exercise", "reps", "weight")
    list_filter = ("exercise", "workout__date")


@admin.register(BodyWeight)
class BodyWeightAdmin(admin.ModelAdmin):
    list_display = ("date", "weight")
    list_filter = ("date",)

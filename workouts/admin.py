from django.contrib import admin
from .models import Exercise, Set, BodyWeight


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ("date", "exercise", "reps", "weight")
    list_filter = ("exercise", "date")
    date_hierarchy = "date"


@admin.register(BodyWeight)
class BodyWeightAdmin(admin.ModelAdmin):
    list_display = ("date", "weight")
    list_filter = ("date",)

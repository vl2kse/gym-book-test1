from django.db import models


class Exercise(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, default="", verbose_name="Описание")

    class Meta:
        ordering = ["name"]
        verbose_name = "Упражнение"
        verbose_name_plural = "Упражнения"

    def __str__(self):
        return self.name


class Workout(models.Model):
    date = models.DateField(verbose_name="Дата")
    notes = models.TextField(blank=True, default="", verbose_name="Заметки")

    class Meta:
        ordering = ["-date"]
        verbose_name = "Тренировка"
        verbose_name_plural = "Тренировки"

    def __str__(self):
        return f"Тренировка от {self.date}"


class Set(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="sets", verbose_name="Тренировка")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="sets", verbose_name="Упражнение")
    reps = models.PositiveIntegerField(verbose_name="Повторения")
    weight = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="Вес (кг)")

    class Meta:
        ordering = ["id"]
        verbose_name = "Подход"
        verbose_name_plural = "Подходы"

    def __str__(self):
        weight_str = f" × {self.weight} кг" if self.weight > 0 else ""
        return f"{self.exercise.name}: {self.reps} раз{weight_str}"


class BodyWeight(models.Model):
    date = models.DateField(unique=True, verbose_name="Дата")
    weight = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Вес (кг)")

    class Meta:
        ordering = ["-date"]
        verbose_name = "Вес тела"
        verbose_name_plural = "Записи веса тела"

    def __str__(self):
        return f"{self.date}: {self.weight} кг"

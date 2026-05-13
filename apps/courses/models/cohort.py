from django.db import models

from apps.core.models import TimeStampModel
from apps.courses.models.course import Course


class StatusChoices(models.TextChoices):
    PREPARING = "PREPARING", "준비중"
    IN_PROGRESS = "IN_PROGRESS", "진행중"
    FINISHED = "FINISHED", "종료"


class Cohort(TimeStampModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="cohorts")
    number = models.PositiveSmallIntegerField()
    max_student = models.PositiveSmallIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PREPARING)

    class Meta:
        db_table = "cohorts"
        unique_together = (("course", "number"),)

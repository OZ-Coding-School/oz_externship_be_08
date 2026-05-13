from django.db import models

from apps.core.models import TimeStampModel
from apps.courses.models.course import Course


class Subject(TimeStampModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="subjects")
    title = models.CharField(max_length=30)
    number_of_days = models.PositiveSmallIntegerField()
    number_of_hours = models.PositiveSmallIntegerField()
    thumbnail_img_url = models.CharField(max_length=255, null=True, blank=True)
    status = models.BooleanField(default=True)

    class Meta:
        db_table = "subjects"
        unique_together = (("course", "title"),)

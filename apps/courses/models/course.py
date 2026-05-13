from django.db import models

from apps.core.models import TimeStampModel


class Course(TimeStampModel):
    name = models.CharField(max_length=30, unique=True)
    tag = models.CharField(max_length=3, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    thumbnail_img_url = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "courses"
        app_label = "courses"

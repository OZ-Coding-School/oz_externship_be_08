from apps.core.models import TimeStampModel
from django.db import models

class Exam(TimeStampModel):
    # subject = models.ForeignKey(Subject,on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    thumbnail_image_url = models.ImageField(max_length=255, default="default_img_url")

    class Meta:
        db_table = "exams"
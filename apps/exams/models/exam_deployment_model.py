from django.db import models

from apps.core.models import TimeStampModel

from .exam_model import Exam


class ExamDeployment(TimeStampModel):

    class ExamStatus(models.TextChoices):
        ON = "activate", "활성화"
        OFF = "deactivate", "비활성화"

    # cohort_id = models.ForeignKey(Cohort,on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    duration_time = models.SmallIntegerField(max_length=2)
    access_code = models.CharField(max_length=64)
    open_at = models.DateTimeField(null=True, blank=True)
    close_at = models.DateTimeField(null=True, blank=True)
    question_snapshot_json = models.JSONField(default=dict)
    status = models.CharField(choices=ExamStatus.choices, max_length=10)

    class Meta:
        db_table = "exam_deployments"

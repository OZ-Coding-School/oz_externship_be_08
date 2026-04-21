from django.conf import settings
from django.db import models

from apps.core.models import TimeStampModel

class Exam(TimeStampModel):
    # subject = models.ForeignKey(Subject,on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    thumbnail_image_url = models.ImageField(max_length=255, default="default_img_url")

    class Meta:
        db_table = "exams"

class ExamQuestion(TimeStampModel):

    class QuestionType(models.TextChoices):
        BLANK = "blank", "빈칸채우기"
        SORT = "sort", "순서정렬"
        CHOICE = "choice", "다지선다"
        SENTENCE = "sentence", "주관식"
        WORD = "word", "단답형"
        QUIZ = "quiz", "OX퀴즈"

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    prompt = models.TextField(null=True, blank=True)
    blank_count = models.SmallIntegerField(max_length=1, null=True, blank=True)
    optional_json = models.TextField(null=True, blank=True)
    type = models.CharField(choices=QuestionType.choices)
    answer = models.JSONField(
        default=dict,
    )
    point = models.SmallIntegerField(max_length=2)
    explantation = models.TextField()

    class Meta:
        db_table = "exam_questions"

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

class ExamSubmission(TimeStampModel):
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    deployment = models.ForeignKey(ExamDeployment, on_delete=models.CASCADE)
    started_at = models.DateTimeField()
    cheating_count = models.SmallIntegerField(max_length=1)
    answer_json = models.JSONField(default=dict)
    score = models.SmallIntegerField()
    correct_answer_count = models.SmallIntegerField()

    class Meta:
        db_table = "exam_submissions"
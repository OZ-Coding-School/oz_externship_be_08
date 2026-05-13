from __future__ import annotations

from typing import Any

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

from apps.core.models import TimeStampModel


class CustomUserManager(BaseUserManager["User"]):
    def create_user(self, email: str, password: str, **extra_fields: Any) -> "User":
        if not email:
            raise ValueError("이메일은 필수항목입니다.")
        email = self.normalize_email(email)
        user: User = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields: Any) -> "User":
        extra_fields["role"] = "ADMIN"
        extra_fields["is_active"] = True
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, TimeStampModel):
    class Gender(models.TextChoices):
        MALE = "M", "남성"
        FEMALE = "F", "여성"

    class Role(models.TextChoices):
        USER = "USER", "일반유저"
        ADMIN = "ADMIN", "관리자"
        STUDENT = "STUDENT", "수강생"

    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(null=False, unique=True)
    name = models.CharField(max_length=30, null=False)
    nickname = models.CharField(max_length=10, null=False, unique=True)
    phone_number = models.CharField(max_length=20, null=False, unique=True)
    gender = models.CharField(choices=Gender.choices, max_length=6, null=True)
    birthday = models.DateField(null=True)
    profile_img_url = models.URLField(max_length=1000, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    role = models.CharField(choices=Role.choices, default=Role.USER)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "nickname", "phone_number"]

    objects = CustomUserManager()

    class Meta:
        db_table = "user"


class SocialUsers(TimeStampModel):
    class Provider(models.TextChoices):
        KAKAO = "kakao", "카카오"
        NAVER = "naver", "네이버"

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="social_users")
    provider = models.CharField(max_length=10, choices=Provider.choices)
    provider_id = models.CharField(max_length=255)

    class Meta:
        db_table = "social_users"


class Withdrawal(TimeStampModel):
    class Reason(models.TextChoices):
        GRADUATION = "GRADUATION", "졸업"
        TRANSFER = "TRANSFER", "다른 플랫폼 이동"
        NO_LONGER_NEEDED = "NO_LONGER_NEEDED", "더 이상 필요하지 않음"
        LACK_OF_INTEREST = "LACK_OF_INTEREST", "흥미 떨어짐"
        TOO_DIFFICULT = "TOO_DIFFICULT", "너무 어려움"
        FOUND_BETTER_SERVICE = "FOUND_BETTER_SERVICE", "더 좋은 서비스 찾음"
        PRIVACY_CONCERNS = "PRIVACY_CONCERNS", "개인정보 우려"
        POOR_SERVICE_QUALITY = "POOR_SERVICE_QUALITY", "서비스 품질 불만"
        TECHNICAL_ISSUES = "TECHNICAL_ISSUES", "기술적 문제"
        LACK_OF_CONTENT = "LACK_OF_CONTENT", "콘텐츠 부족"
        OTHER = "OTHER", "기타"

    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name="withdrawal")
    reason = models.CharField(max_length=20, choices=Reason.choices)
    reason_detail = models.TextField(blank=True, default="")
    due_date = models.DateField()

    class Meta:
        db_table = "withdrawal"


class StudentEnrollmentRequests(TimeStampModel):
    class Status(models.TextChoices):
        PENDING = "pending", "대기중"
        ACCEPTED = "accepted", "승인됨"
        REJECTED = "rejected", "거절됨"
        CANCELED = "canceled", "취소됨"

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollment_requests", null=False)
    cohort = models.ForeignKey("courses.Cohort", on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING, null=False)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "student_enrollment_requests"


class CohortStudents(TimeStampModel):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cohort_students", null=False)
    cohort = models.ForeignKey("courses.Cohort", on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "cohort_students"


class OperationManagers(TimeStampModel):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="operation_managers", null=False)
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, null=True)
    # course 디렉토리 변경으로 인한 FK 경로 posts.Course -> course.Course로 수정

    class Meta:
        db_table = "operation_managers"


class LearningCoachs(TimeStampModel):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="learning_coachs", null=False)
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, null=True)
    # course 디렉토리 변경으로 인한 FK 경로 posts.Course -> course.Course로 수정

    class Meta:
        db_table = "learning_coachs"


class TrainigAssistants(TimeStampModel):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="training_assistants", null=False)
    cohort = models.ForeignKey("courses.Cohort", on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "training_assistants"

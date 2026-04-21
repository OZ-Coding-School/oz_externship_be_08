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
        ADMIN = "ADMIN", "어드민"
        STUDENT = "STUDENT", "수강생"

    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(null=False, unique=True)
    name = models.CharField(max_length=30, null=False)
    nickname = models.CharField(max_length=10, null=False, unique=True)
    phone_number = models.CharField(max_length=20, null=False, unique=True)
    gender = models.CharField(max_length=6, null=True, choices=Gender.choices)
    birthday = models.DateField(null=True)
    profile_img_url = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=False)
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
        GRADUATION = "graduation", "졸업"
        TRANSFER = "transfer", "다른 플랫폼 이동"
        NO_LONGER_NEEDED = "no_longer_needed", "더 이상 필요없음"
        LACK_OF_INTEREST = "lack_of_interest", "흥미 떨어짐"
        TOO_DIFFICULT = "too_difficult", "너무 어려움"
        FOUND_BETTER_SERVICE = "found_better_service", "더 좋은 서비스 찾음"
        PRIVACY_CONCERNS = "privacy_concerns", "개인정보 우려"
        POOR_SERVICE_QUALITY = "poor_service_quality", "서비스 품질 불만"
        TECHNICAL_ISSUES = "technical_issue", "기술적 문제"
        LACK_OF_CONTENT = "lack_of_content", "콘텐츠 부족"
        OTHER = "other", "기타"

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="withdrawals")
    reason = models.CharField(max_length=20, choices=Reason.choices)
    reason_detail = models.TextField()
    due_date = models.DateField()

    class Meta:
        db_table = "withdrawal"


class StudentEnrollmentRequests(TimeStampModel):
    class Status(models.TextChoices):
        END = "end", "종료됨"
        ONGOING = "ongoing", "진행중"
        PENDING = "pending", "대기중"

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollment_requests", null=False)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING, null=False)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "student_enrollment_requests"


class CohortStudents(TimeStampModel):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cohort_students", null=False)

    class Meta:
        db_table = "cohort_students"


class OperationManagers(TimeStampModel):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="operation_managers", null=False)

    class Meta:
        db_table = "operation_managers"


class LearningCoachs(TimeStampModel):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="learning_coachs", null=False)

    class Meta:
        db_table = "learning_coachs"


class TrainigAssistants(TimeStampModel):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="training_assistants", null=False)

    class Meta:
        db_table = "training_assistants"

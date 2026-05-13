from typing import Any

from django.urls import reverse
from django.utils import timezone
from rest_framework import serializers

from apps.courses.models.cohort import Cohort
from apps.courses.models.course import Course
from apps.courses.models.subject import Subject
from apps.exams.models.exam_deployment_model import ExamDeployment
from apps.exams.models.exam_model import Exam


class SubjectSummarySerializer(serializers.ModelSerializer[Subject]):
    class Meta:
        model = Subject
        fields = ["id", "title"]


class ExamSummarySerializer(serializers.ModelSerializer[Exam]):
    class Meta:
        model = Exam
        fields = ["id", "title", "thumbnail_img_url"]


class CourseSummarySerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ["id", "name", "tag"]


class CohortSummarySerializer(serializers.ModelSerializer[Cohort]):
    course = CourseSummarySerializer()
    display = serializers.SerializerMethodField()

    def get_display(self, obj: Cohort) -> str:
        return f"{obj.course.name} {obj.number}기"

    class Meta:
        model = Cohort
        fields = ["id", "number", "display", "course"]


class AdminExamDeploymentCreateSerializer(serializers.Serializer[Any]):
    exam_id = serializers.IntegerField()
    cohort_id = serializers.IntegerField()
    duration_time = serializers.IntegerField(
        min_value=1,
        max_value=99,
        default=60,
    )
    open_at = serializers.DateTimeField()
    close_at = serializers.DateTimeField()

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        now = timezone.now()

        if data["open_at"] < now:
            raise serializers.ValidationError({"error_detail": "유효하지 않은 배포 생성 요청입니다."})
        if data["close_at"] < now:
            raise serializers.ValidationError({"error_detail": "유효하지 않은 배포 생성 요청입니다."})
        if data["open_at"] >= data["close_at"]:
            raise serializers.ValidationError({"error_detail": "유효하지 않은 배포 생성 요청입니다."})
        return data


class AdminExamDeploymentListSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    submit_count = serializers.IntegerField()
    avg_score = serializers.FloatField(allow_null=True)
    exam = ExamSummarySerializer()
    subject = SubjectSummarySerializer(source="exam.subject")
    cohort = CohortSummarySerializer()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()


class AdminExamDeploymentListResponseSerializer(serializers.Serializer[Any]):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = AdminExamDeploymentListSerializer(many=True)


class AdminExamDeploymentListQuerySerializer(serializers.Serializer[Any]):
    subject_id = serializers.IntegerField(required=False)
    cohort_id = serializers.IntegerField(required=False)
    search_keyword = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )
    sort = serializers.ChoiceField(
        choices=["created_at", "submit_count", "avg_score"],
        required=False,
        default="created_at",
    )
    order = serializers.ChoiceField(
        choices=["asc", "desc"],
        required=False,
        default="desc",
    )


class AdminExamDeploymentDetailPathSerializer(serializers.Serializer[Any]):
    deployment_id = serializers.IntegerField(min_value=1)


class AdminExamDeploymentDetailSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    exam_access_url = serializers.SerializerMethodField()
    access_code = serializers.CharField()
    cohort = CohortSummarySerializer()
    submit_count = serializers.IntegerField()
    not_submitted_count = serializers.IntegerField()
    duration_time = serializers.IntegerField()
    open_at = serializers.DateTimeField()
    close_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
    exam = ExamSummarySerializer()
    subject = SubjectSummarySerializer(source="exam.subject")

    def get_exam_access_url(self, obj: Any) -> str:
        return reverse("exam-deployment-detail", kwargs={"deployment_id": obj.id})


class AdminExamDeploymentUpdateSerializer(serializers.Serializer[Any]):
    open_at = serializers.DateTimeField()
    close_at = serializers.DateTimeField()
    duration_time = serializers.IntegerField(
        min_value=1,
        max_value=99,
    )

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        now = timezone.now()

        if data["open_at"] < now:
            raise serializers.ValidationError({"error_detail": "유효하지 않은 배포 수정 요청입니다."})
        if data["close_at"] < now:
            raise serializers.ValidationError({"error_detail": "유효하지 않은 배포 수정 요청입니다."})
        if data["open_at"] >= data["close_at"]:
            raise serializers.ValidationError({"error_detail": "유효하지 않은 배포 수정 요청입니다."})
        return data


class AdminExamDeploymentUpdateResponseSerializer(serializers.ModelSerializer[ExamDeployment]):
    deployment_id = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = ExamDeployment
        fields = ["deployment_id", "duration_time", "open_at", "close_at", "updated_at"]
        read_only_fields = ["duration_time", "open_at", "close_at", "updated_at"]


class AdminExamDeploymentStatusSerializer(serializers.Serializer[Any]):
    status = serializers.ChoiceField(choices=ExamDeployment.ExamStatus.choices)


class AdminExamDeploymentStatusResponseSerializer(serializers.ModelSerializer[ExamDeployment]):
    deployment_id = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = ExamDeployment
        fields = ["deployment_id", "status"]
        read_only_fields = ["status"]

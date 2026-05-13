from __future__ import annotations

from typing import Any

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.courses.models.cohort import Cohort
from apps.courses.models.course import Course
from apps.users.models import User, Withdrawal

POSITION_CHOICES = ("TA", "OM", "LC", "ENROLLED")


class UserPositionMixin:
    def _get_position(self, user: User) -> str | None:
        for manager, position in (
            (user.training_assistants, "TA"),
            (user.operation_managers, "OM"),
            (user.learning_coachs, "LC"),
        ):
            if bool(manager.all()):
                return position
        if bool(user.cohort_students.all()) or user.role == User.Role.STUDENT:
            return "ENROLLED"
        return None


class WithdrawalListQuerySerializer(serializers.Serializer[Any]):
    page = serializers.IntegerField(required=False, default=1, min_value=1)
    page_size = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100)
    search = serializers.CharField(required=False, allow_blank=True)
    role = serializers.ChoiceField(required=False, choices=User.Role.choices)
    position = serializers.ChoiceField(required=False, choices=POSITION_CHOICES)
    sort = serializers.ChoiceField(required=False, choices=("latest", "oldest"))


class WithdrawalListUserSerializer(UserPositionMixin, serializers.ModelSerializer[User]):
    position = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "name", "role", "position", "birthday"]
        read_only_fields = fields

    @extend_schema_field(serializers.ChoiceField(choices=POSITION_CHOICES, allow_null=True))
    def get_position(self, obj: User) -> str | None:
        return self._get_position(obj)


class WithdrawalListSerializer(serializers.ModelSerializer[Withdrawal]):
    user = WithdrawalListUserSerializer(read_only=True)
    reason_display = serializers.CharField(source="get_reason_display", read_only=True)
    withdrawn_at = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = Withdrawal
        fields = ["id", "user", "reason", "reason_display", "withdrawn_at"]
        read_only_fields = fields


class CourseNestedSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ["id", "name", "tag"]
        read_only_fields = fields


class CohortNestedSerializer(serializers.ModelSerializer[Cohort]):
    class Meta:
        model = Cohort
        fields = ["id", "number", "status", "start_date", "end_date"]
        read_only_fields = fields


class AssignedCourseSerializer(serializers.Serializer[Any]):
    course = CourseNestedSerializer(read_only=True)
    cohort = CohortNestedSerializer(read_only=True)


class WithdrawalDetailUserSerializer(UserPositionMixin, serializers.ModelSerializer[User]):
    position = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "nickname",
            "name",
            "gender",
            "role",
            "position",
            "status",
            "profile_img_url",
            "created_at",
        ]
        read_only_fields = fields

    @extend_schema_field(serializers.ChoiceField(choices=POSITION_CHOICES, allow_null=True))
    def get_position(self, obj: User) -> str | None:
        return self._get_position(obj)

    def get_status(self, obj: User) -> str:
        try:
            obj.withdrawal
            return "WITHDREW"
        except Withdrawal.DoesNotExist:
            pass
        if obj.is_active:
            return "ACTIVATED"
        return "DEACTIVATED"

    def to_representation(self, instance: User) -> dict[str, Any]:
        data = super().to_representation(instance)
        data["gender"] = data.get("gender") or ""
        data["profile_img_url"] = data.get("profile_img_url") or ""
        return data


class WithdrawalDetailSerializer(serializers.ModelSerializer[Withdrawal]):
    user = WithdrawalDetailUserSerializer(read_only=True)
    assigned_courses = serializers.SerializerMethodField()
    reason_display = serializers.CharField(source="get_reason_display", read_only=True)
    withdrawn_at = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = Withdrawal
        fields = [
            "id",
            "user",
            "assigned_courses",
            "reason",
            "reason_display",
            "reason_detail",
            "due_date",
            "withdrawn_at",
        ]
        read_only_fields = fields

    @extend_schema_field(AssignedCourseSerializer(many=True))
    def get_assigned_courses(self, obj: Withdrawal) -> list[dict[str, Any]]:
        if obj.user is None:
            return []

        assigned_courses: list[dict[str, Any]] = []
        self._append_cohort_relations(assigned_courses, obj.user.cohort_students)
        self._append_cohort_relations(assigned_courses, obj.user.training_assistants)
        self._append_course_relations(assigned_courses, obj.user.operation_managers)
        self._append_course_relations(assigned_courses, obj.user.learning_coachs)
        return assigned_courses

    def _append_cohort_relations(self, result: list[dict[str, Any]], manager: Any) -> None:
        for relation in manager.all():
            self._append_assigned_course(result, relation.cohort)

    def _append_course_relations(self, result: list[dict[str, Any]], manager: Any) -> None:
        for relation in manager.all():
            self._append_course_cohorts(result, relation.course)

    def _append_assigned_course(self, result: list[dict[str, Any]], cohort: Cohort | None) -> None:
        if cohort is None:
            return
        result.append(AssignedCourseSerializer({"course": cohort.course, "cohort": cohort}).data)

    def _append_course_cohorts(self, result: list[dict[str, Any]], course: Course | None) -> None:
        if course is None:
            return
        for cohort in course.cohorts.all():
            self._append_assigned_course(result, cohort)


class WithdrawalListResponseSerializer(serializers.Serializer[Any]):
    count = serializers.IntegerField(read_only=True)
    next = serializers.CharField(read_only=True, allow_null=True)
    previous = serializers.CharField(read_only=True, allow_null=True)
    results = WithdrawalListSerializer(many=True, read_only=True)


class WithdrawalCancelResponseSerializer(serializers.Serializer[Any]):
    detail = serializers.CharField(read_only=True)


class ValidationErrorDetailSerializer(serializers.Serializer[Any]):
    error_detail = serializers.DictField(child=serializers.ListField(child=serializers.CharField()), read_only=True)


class ErrorDetailSerializer(serializers.Serializer[Any]):
    error_detail = serializers.CharField(read_only=True)

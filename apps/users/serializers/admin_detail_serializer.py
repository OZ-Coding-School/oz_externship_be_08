from typing import Any

from rest_framework import serializers

from apps.courses.models.course import Course
from apps.users.models import CohortStudents, User
from apps.users.serializers.available_courses_serializer import CohortInfoSerializer


class AdminCourseWithTagSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ["id", "name", "tag"]
        read_only_fields = ["id", "name", "tag"]


class AdminAssignedCourseSerializer(serializers.ModelSerializer[CohortStudents]):
    course = AdminCourseWithTagSerializer(source="cohort.course", read_only=True)
    cohort = CohortInfoSerializer(read_only=True)

    class Meta:
        model = CohortStudents
        fields = ["course", "cohort"]


_DETAIL_FIELDS = [
    "id",
    "email",
    "nickname",
    "name",
    "phone_number",
    "birthday",
    "gender",
    "status",
    "role",
    "profile_img_url",
    "assigned_courses",
    "created_at",
]


class AdminAccountDetailSerializer(serializers.ModelSerializer[User]):
    status = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    assigned_courses = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = _DETAIL_FIELDS
        read_only_fields = _DETAIL_FIELDS

    @staticmethod
    def get_status(obj: User) -> str:
        if hasattr(obj, "withdrawal"):
            return "withdrew"
        return "active" if obj.is_active else "inactive"

    @staticmethod
    def get_role(obj: User) -> str:
        return obj.role.lower()

    @staticmethod
    def get_assigned_courses(obj: User) -> list[dict[str, Any]]:
        cohort_students = obj.cohort_students.all()
        ser = AdminAssignedCourseSerializer(cohort_students, many=True)
        return list(ser.data)

from typing import Any

from django.db.models import QuerySet

from apps.courses.models.course import Course
from apps.courses.utils.exceptions import (
    CourseAlreadyExistsError,
    CourseNotFoundError,
)


def get_course_list() -> QuerySet[Course]:
    return Course.objects.all().order_by("id")


def get_course_detail(course_id: int) -> Course:
    try:
        return Course.objects.get(id=course_id)
    except Course.DoesNotExist as e:
        raise CourseNotFoundError("과정을 찾을 수 없습니다.") from e


def create_course(validated_data: dict[str, Any]) -> Course:
    name = validated_data["name"]

    if Course.objects.filter(name=name).exists():
        raise CourseAlreadyExistsError("이미 등록된 과정명입니다.")

    return Course.objects.create(**validated_data)


def update_course(course_id: int, validated_data: dict[str, Any]) -> Course:
    course = get_course_detail(course_id)

    # 수정된 데이터 반영
    for key, value in validated_data.items():
        setattr(course, key, value)

    # 수정된 필드만 저장 (update_fields)
    course.save(update_fields=validated_data.keys())
    return course


def delete_course(course_id: int) -> None:
    course = get_course_detail(course_id)
    course.delete()

from typing import Any

from rest_framework import serializers

from apps.courses.models.course import Course


class CourseListResponseSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ["id", "name", "tag", "thumbnail_img_url"]


class CourseCreateRequestSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ["name", "tag", "description", "thumbnail_img_url"]
        extra_kwargs: dict[str, Any] = {
            "name": {"validators": []},  # unique validator 끔 (service에서 처리)
        }


class CourseCreateResponseSerializer(serializers.Serializer[Any]):
    detail = serializers.CharField()
    id = serializers.IntegerField()


class CourseDetailResponseSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "tag",
            "description",
            "thumbnail_img_url",
            "created_at",
            "updated_at",
        ]


class CourseUpdateRequestSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ["name", "tag", "description", "thumbnail_img_url"]
        extra_kwargs = {
            "name": {"required": False},
            "tag": {"required": False},
            "description": {"required": False},
            "thumbnail_img_url": {"required": False},
        }


class CourseUpdateResponseSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "tag",
            "description",
            "thumbnail_img_url",
            "updated_at",
        ]


class CourseDeleteResponseSerializer(serializers.Serializer[Any]):
    detail = serializers.CharField()


class ErrorResponseSerializer(serializers.Serializer[Any]):
    error_detail = serializers.CharField()


class ValidationErrorResponseSerializer(serializers.Serializer[Any]):
    error_detail = serializers.DictField()

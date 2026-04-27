from typing import Any

from rest_framework import serializers


class ExamPresignedUrlRequestSerializer(serializers.Serializer[dict[str, Any]]):
    file_name = serializers.CharField()


class ExamPresignedUrlResponseSerializer(serializers.Serializer[dict[str, Any]]):
    presigned_url = serializers.CharField()
    img_url = serializers.CharField()
    key = serializers.CharField()


class ExamErrorResponseSerializer(serializers.Serializer[dict[str, Any]]):
    error_detail = serializers.CharField()

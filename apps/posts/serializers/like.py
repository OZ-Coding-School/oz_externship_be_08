from typing import Any

from rest_framework import serializers


class PostLikeCreateResponseSerializer(serializers.Serializer[dict[str, Any]]):
    detail = serializers.CharField(default="좋아요가 등록되었습니다.")


class PostLikeCancelResponseSerializer(serializers.Serializer[dict[str, Any]]):
    detail = serializers.CharField(default="좋아요가 취소되었습니다.")


class PostLikeErrorResponseSerializer(serializers.Serializer[dict[str, Any]]):
    error_detail = serializers.CharField()

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema

from apps.qna.serializers.category_serializers import (
    CategoryTreeSerializer,
)

# 유저 카테고리 목록 조회
category_list_schema = extend_schema(
    tags=["qna"],
    summary="유저 카테고리 목록 조회",
    description="카테고리 목록을 트리 구조로 조회합니다.",
    responses={
        200: CategoryTreeSerializer,
        401: OpenApiResponse(description="로그인이 필요합니다."),
        403: OpenApiResponse(description="카테고리 조회 권한이 없습니다."),
    },
)

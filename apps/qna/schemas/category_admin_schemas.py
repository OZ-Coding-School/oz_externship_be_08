from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema

from apps.qna.serializers.category_serializers import (
    AdminCategoryCreateResponseSerializer,
    AdminCategoryCreateSerializer,
    AdminCategoryListSerializer,
)

# 어드민 카테고리 생성
admin_category_create_schema = extend_schema(
    tags=["admin-qna"],
    summary="어드민 카테고리 생성",
    description="어드민이 카테고리를 생성합니다.",
    request=AdminCategoryCreateSerializer,
    responses={
        201: AdminCategoryCreateResponseSerializer,
        400: OpenApiResponse(description="카테고리 종류와 이름은 필수 입력값입니다."),
        401: OpenApiResponse(description="로그인이 필요합니다."),
        403: OpenApiResponse(description="카테고리 등록 권한이 없습니다."),
        404: OpenApiResponse(description="부모 카테고리를 찾을 수 없습니다."),
        409: OpenApiResponse(description="동일한 이름의 카테고리가 이미 존재합니다."),
    },
)

# 어드민 카테고리 목록 조회
admin_category_list_schema = extend_schema(
    tags=["admin-qna"],
    summary="어드민 카테고리 목록 조회",
    description="어드민이 카테고리 목록을 조회합니다.",
    parameters=[
        OpenApiParameter(name="page", type=int, description="페이지 번호"),
        OpenApiParameter(name="page_size", type=int, description="페이지 크기"),
        OpenApiParameter(name="search_keyword", type=str, description="검색 키워드"),
        OpenApiParameter(
            name="category_type",
            type=str,
            description="카테고리 종류 (large, middle, small)",
        ),
    ],
    responses={
        200: AdminCategoryListSerializer,
        400: OpenApiResponse(description="유효하지 않은 목록 조회 요청입니다."),
        401: OpenApiResponse(description="로그인이 필요합니다."),
        403: OpenApiResponse(description="카테고리 목록 조회 권한이 없습니다."),
    },
)

# 어드민 카테고리 삭제
admin_category_delete_schema = extend_schema(
    tags=["admin-qna"],
    summary="어드민 카테고리 삭제",
    description="어드민이 카테고리를 삭제합니다. 하위 카테고리도 함께 삭제되며 질문은 기본 카테고리로 이관됩니다.",
    responses={
        200: OpenApiResponse(description="카테고리 삭제 성공"),
        401: OpenApiResponse(description="로그인이 필요합니다."),
        403: OpenApiResponse(description="카테고리 삭제 권한이 없습니다."),
        404: OpenApiResponse(description="해당 카테고리를 찾을 수 없습니다."),
        409: OpenApiResponse(description="기본 카테고리는 삭제할 수 없습니다."),
    },
)

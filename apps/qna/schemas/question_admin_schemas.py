from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema

from apps.qna.serializers.admin_question_serializers import (
    AdminQuestionDeleteResponseSerializer,
    AdminQuestionDetailSerializer,
    AdminQuestionListItemSerializer,
)

# ── 어드민 질문 삭제 ──────────────────────────────────────────────────

admin_question_delete_schema = extend_schema(
    tags=["Admin-Qna"],
    summary="어드민 질의응답 삭제",
    description="관리자가 질의응답을 삭제합니다. 연관된 답변과 댓글도 함께 삭제됩니다.",
    parameters=[
        OpenApiParameter(
            name="question_id",
            type=int,
            location=OpenApiParameter.PATH,
            description="질문 ID",
            required=True,
        ),
    ],
    responses={
        200: AdminQuestionDeleteResponseSerializer,
        400: OpenApiResponse(description="유효하지 않은 삭제 요청입니다."),
        401: OpenApiResponse(description="로그인이 필요합니다."),
        403: OpenApiResponse(description="질의응답 삭제 권한이 없습니다."),
        404: OpenApiResponse(description="삭제할 질문을 찾을 수 없습니다."),
    },
)

# ── 어드민 질문 상세 조회 ────────────────────────────────────────────

admin_question_detail_schema = extend_schema(
    tags=["Admin-Qna"],
    summary="어드민 질의응답 상세 조회",
    description="관리자가 질의응답 상세 정보를 조회합니다.",
    parameters=[
        OpenApiParameter(
            name="question_id",
            type=int,
            location=OpenApiParameter.PATH,
            description="질문 ID",
            required=True,
        ),
    ],
    responses={
        200: AdminQuestionDetailSerializer,
        400: OpenApiResponse(description="유효하지 않은 상세 조회 요청입니다."),
        401: OpenApiResponse(description="로그인이 필요합니다."),
        403: OpenApiResponse(description="질의응답 상세 조회 권한이 없습니다."),
        404: OpenApiResponse(description="해당 질문을 찾을 수 없습니다."),
    },
)

# ── 어드민 질문 목록 조회 ────────────────────────────────────────────

admin_question_list_schema = extend_schema(
    tags=["Admin-Qna"],
    summary="어드민 질의응답 목록 조회",
    description="관리자가 질의응답 목록을 조회합니다. 페이지네이션, 검색, 필터링을 지원합니다.",
    parameters=[
        OpenApiParameter(
            name="page",
            type=int,
            location=OpenApiParameter.QUERY,
            description="페이지 번호 (기본값: 1)",
            required=False,
        ),
        OpenApiParameter(
            name="page_size",
            type=int,
            location=OpenApiParameter.QUERY,
            description="페이지 크기 (기본값: 20, 최대: 100)",
            required=False,
        ),
        OpenApiParameter(
            name="search_keyword",
            type=str,
            location=OpenApiParameter.QUERY,
            description="검색 키워드 (제목 검색)",
            required=False,
        ),
        OpenApiParameter(
            name="category_id",
            type=int,
            location=OpenApiParameter.QUERY,
            description="카테고리 ID (하위 카테고리 포함)",
            required=False,
        ),
        OpenApiParameter(
            name="answer_status",
            type=str,
            location=OpenApiParameter.QUERY,
            description="답변 상태 필터 (Y: 답변 있음, N: 답변 없음)",
            required=False,
        ),
        OpenApiParameter(
            name="sort",
            type=str,
            location=OpenApiParameter.QUERY,
            description="정렬 기준 (latest: 최신순, oldest: 오래된순, views: 조회수순, 기본값: latest)",
            required=False,
        ),
    ],
    responses={
        200: AdminQuestionListItemSerializer(many=True),
        400: OpenApiResponse(description="유효하지 않은 목록 조회 요청입니다."),
        401: OpenApiResponse(description="로그인이 필요합니다."),
        403: OpenApiResponse(description="질의응답 목록 조회 권한이 없습니다."),
    },
)

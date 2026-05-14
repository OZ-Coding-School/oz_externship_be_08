from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)

from apps.qna.serializers.question_serializers import (
    QuestionCreateResponseSerializer,
    QuestionCreateSerializer,
    QuestionDetailSerializer,
    QuestionListItemSerializer,
    QuestionUpdateResponseSerializer,
    QuestionUpdateSerializer,
)

# ── 질문 등록 ──────────────────────────────────────────────────────

question_create_schema = extend_schema(
    tags=["qna"],
    summary="질문 등록",
    description="새로운 질문을 등록합니다. 소분류 카테고리만 선택 가능합니다.",
    request=QuestionCreateSerializer,
    responses={
        201: QuestionCreateResponseSerializer,
        400: OpenApiResponse(description="유효하지 않은 질문 등록 요청입니다."),
        401: OpenApiResponse(description="로그인한 수강생만 질문을 등록할 수 있습니다."),
        403: OpenApiResponse(description="질문 등록 권한이 없습니다."),
    },
)

# ── 질문 목록 조회 ──────────────────────────────────────────────────

question_list_schema = extend_schema(
    tags=["qna"],
    summary="질문 목록 조회",
    description="질의응답 목록을 조회합니다. 검색, 카테고리 필터, 답변 상태 필터, 정렬 기능을 제공합니다.",
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
            description="페이지당 항목 수 (기본값: 10, 최대: 100)",
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
            description="카테고리 ID (상위 카테고리 선택 시 하위 카테고리 포함)",
            required=False,
        ),
        OpenApiParameter(
            name="answer_status",
            type=str,
            location=OpenApiParameter.QUERY,
            description="답변 상태 필터 (answered: 답변 있음, unanswered: 답변 없음)",
            required=False,
            enum=["answered", "unanswered"],
        ),
        OpenApiParameter(
            name="sort",
            type=str,
            location=OpenApiParameter.QUERY,
            description="정렬 기준 (latest: 최신순, oldest: 오래된순, views: 조회수순)",
            required=False,
            enum=["latest", "oldest", "views"],
        ),
    ],
    responses={
        200: QuestionListItemSerializer(many=True),
        400: OpenApiResponse(description="유효하지 않은 목록 조회 요청입니다."),
    },
)

# ── 질문 상세 조회 ──────────────────────────────────────────────────

question_detail_schema = extend_schema(
    tags=["qna"],
    summary="질문 상세 조회",
    description="질문의 상세 정보를 조회합니다. 조회 시 조회수가 1 증가합니다.",
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
        200: QuestionDetailSerializer,
        400: OpenApiResponse(description="유효하지 않은 질문 상세 조회 요청입니다."),
        401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
        403: OpenApiResponse(description="권한이 없습니다."),
        404: OpenApiResponse(description="해당 질문을 찾을 수 없습니다."),
    },
)

# ── 질문 수정 ──────────────────────────────────────────────────────

question_update_schema = extend_schema(
    tags=["qna"],
    summary="질문 수정",
    description="본인이 작성한 질문을 수정합니다. 소분류 카테고리만 선택 가능합니다.",
    parameters=[
        OpenApiParameter(
            name="question_id",
            type=int,
            location=OpenApiParameter.QUERY,
            description="질문 ID",
            required=True,
        ),
    ],
    request=QuestionUpdateSerializer,
    responses={
        200: QuestionUpdateResponseSerializer,
        400: OpenApiResponse(description="유효하지 않은 질문 수정 요청입니다."),
        401: OpenApiResponse(description="로그인한 사용자만 질문을 수정할 수 있습니다."),
        403: OpenApiResponse(description="본인이 작성한 질문만 수정할 수 있습니다."),
        404: OpenApiResponse(description="해당 질문을 찾을 수 없습니다."),
    },
)

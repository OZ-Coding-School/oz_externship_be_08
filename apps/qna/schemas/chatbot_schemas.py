from drf_spectacular.utils import OpenApiResponse, extend_schema

from apps.qna.serializers.chatbot_serializers import (
    HistoryResponseSerializer,
    InitialAIAnswerSerializer,
    QNAChatbotListResponseSerializer,
)

ai_answer_post_schema = extend_schema(
    tags=["chatbot"],
    summary="AI 초기응답 생성",
    description="질문글을 기준으로 AI가 초기응답을 생성합니다.",
    responses={
        201: InitialAIAnswerSerializer,
        401: OpenApiResponse(description="로그인한 사용자만 요청할 수 있습니다."),
        404: OpenApiResponse(description="질문 데이터를 찾을 수 없습니다."),
        409: OpenApiResponse(description="이미 AI가 답변을 생성했습니다."),
        502: OpenApiResponse(description="외부 API 호출에 실패했습니다."),
        504: OpenApiResponse(description="외부 API 응답 시간이 초과되었습니다."),
    },
)

ai_answer_get_schema = extend_schema(
    tags=["chatbot"],
    summary="AI 초기응답 조회",
    description="캐시에 저장된 초기응답을 불러옵니다.",
    responses={
        200: InitialAIAnswerSerializer,
        401: OpenApiResponse(description="로그인한 사용자만 요청할 수 있습니다."),
        404: OpenApiResponse(description="질문 데이터를 찾을 수 없습니다."),
        408: OpenApiResponse(description="응답 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요."),
        409: OpenApiResponse(description="이미 AI가 답변을 생성했습니다."),
        502: OpenApiResponse(description="외부 API 호출에 실패했습니다."),
        504: OpenApiResponse(description="외부 API 응답 시간이 초과되었습니다."),
    },
)


qna_chatbot_post_schema = extend_schema(
    tags=["chatbot"],
    summary="qna 챗봇 대화",
    description="활성화된 채팅창에서 qna 챗봇과 질의응답을 합니다.",
    responses={
        200: OpenApiResponse(description="SSE 스트림 (text/event-stream)"),
        401: OpenApiResponse(description="로그인한 사용자만 이용할 수 있습니다."),
        404: OpenApiResponse(description="해당 질문을 찾을 수 없습니다."),
        429: OpenApiResponse(description="더 필요한 질문은 질문 게시판을 이용해 주세요."),
        502: OpenApiResponse(description="외부 API 호출에 실패했습니다."),
        504: OpenApiResponse(description="외부 API 응답 시간이 초과되었습니다."),
    },
)

qna_chatbot_get_schema = extend_schema(
    tags=["chatbot"],
    summary="qna 챗봇 히스토리 조회",
    description="캐시에 저장된 히스토리를 불러옵니다.",
    responses={
        200: HistoryResponseSerializer(many=True),
        401: OpenApiResponse(description="로그인한 사용자만 이용할 수 있습니다."),
        404: OpenApiResponse(description="해당 질문을 찾을 수 없습니다."),
        429: OpenApiResponse(description="더 필요한 질문은 질문 게시판을 이용해 주세요."),
        502: OpenApiResponse(description="외부 API 호출에 실패했습니다."),
        504: OpenApiResponse(description="외부 API 응답 시간이 초과되었습니다."),
    },
)

qna_chatbot_list_schema = extend_schema(
    tags=["chatbot"],
    summary="qna 챗봇 리스트 조회",
    description="대화창별 마지막 메시지를 불러옵니다.",
    responses={
        200: QNAChatbotListResponseSerializer(many=True),
        502: OpenApiResponse(description="외부 API 호출에 실패했습니다."),
        504: OpenApiResponse(description="외부 API 응답 시간이 초과되었습니다."),
    },
)


cs_chatbot_get_schema = extend_schema(
    tags=["chatbot"],
    summary="cs 챗봇 상세 조회",
    description="cs 챗봇의 히스토리를 불러와서 조회합니다.",
    responses={
        200: HistoryResponseSerializer(many=True),
    },
)

cs_chatbot_post_schema = extend_schema(
    tags=["chatbot"],
    summary="cs 챗봇 대화",
    description="활성화된 채팅창에서 cs 챗봇에게 고객지원을 받습니다.",
    responses={
        200: OpenApiResponse(description="SSE 스트림 (text/event-stream)"),
    },
)

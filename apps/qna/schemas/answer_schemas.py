from drf_spectacular.utils import OpenApiResponse, extend_schema

from apps.qna.serializers.answer_serializers import (
    AnswerAcceptResponseSerializer,
    AnswerCommentRequestSerializer,
    AnswerCommentResponseSerializer,
    AnswerRequestSerializer,
    AnswerResponseSerializer,
    AnswerUpdateSerializer,
)

answer_accept_schema = extend_schema(
    tags=["qna"],
    summary="답변 채택",
    description="질문 작성자가 답변을 채택합니다",
    responses={
        200: AnswerAcceptResponseSerializer,
        401: OpenApiResponse(description="로그인한 사용자만 채택할 수 있습니다."),
        403: OpenApiResponse(description="본인의 질문에 대한 답변만 채택할 수 있습니다."),
        404: OpenApiResponse(description="해당 질문 또는 답변을 찾을 수 없습니다."),
        409: OpenApiResponse(description="이미 채택된 답변이 존재합니다."),
    },
)

answer_create_schema = extend_schema(
    tags=["qna"],
    summary="답변 등록",
    description="질문에 대한 답변을 등록합니다.",
    request=AnswerRequestSerializer,
    responses={
        201: AnswerResponseSerializer,
        400: OpenApiResponse(description="잘못된 요청 입니다."),
        401: OpenApiResponse(description="로그인한 사용자만 채택할 수 있습니다."),
        403: OpenApiResponse(description="답변 작성 권한이 없습니다."),
        404: OpenApiResponse(description="해당 질문을 찾을 수 없습니다."),
    },
)
answer_update_schema = extend_schema(
    tags=["qna"],
    summary="답변 수정",
    description="질문에 대한 답변을 수정합니다.",
    request=AnswerRequestSerializer,
    responses={
        200: AnswerUpdateSerializer,
        401: OpenApiResponse(description="로그인한 사용자만 답변을 수정할 수 있습니다."),
        403: OpenApiResponse(description="본인이 작성한 답변만 수정할 수 있습니다."),
        404: OpenApiResponse(description="해당 답변을 찾을 수 없습니다."),
    },
)

answer_comment_schema = extend_schema(
    tags=["qna"],
    summary="답변 댓글",
    description="질문에 대한 댓글 작성",
    request=AnswerCommentRequestSerializer,
    responses={
        200: AnswerCommentResponseSerializer,
        400: OpenApiResponse(description="댓글 내용은 1~500자 사이로 입력해야 합니다."),
        401: OpenApiResponse(description="로그인한 사용자만 댓글을 작성할 수 있습니다."),
        403: OpenApiResponse(description="댓글 작성 권한이 없습니다."),
        404: OpenApiResponse(description="해당 답변을 찾을 수 없습니다."),
    },
)

from typing import Any, NoReturn

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import (
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.presigned_url.serializers import (
    PresignedUrlRequestSerializer,
    PresignedUrlResponseSerializer,
)
from apps.core.utils.permissions import IsStudentUser
from apps.core.utils.s3 import PresignedUrlView
from apps.core.utils.types import AuthenticatedRequest
from apps.qna.exceptions import BaseCustomException
from apps.qna.schemas.answer_schemas import (
    answer_accept_schema,
    answer_comment_schema,
    answer_create_schema,
    answer_update_schema,
)
from apps.qna.serializers.answer_serializers import (
    AnswerAcceptResponseSerializer,
    AnswerCommentRequestSerializer,
    AnswerCommentResponseSerializer,
    AnswerRequestSerializer,
    AnswerResponseSerializer,
    AnswerUpdateSerializer,
)
from apps.qna.services.answer_services import (
    AnswerAcceptService,
    AnswerCommentService,
    AnswerDetailService,
    AnswerService,
)


@extend_schema(
    tags=["qna"],
    summary="답변 이미지 presigned URL 발급",
    request=PresignedUrlRequestSerializer,
    responses={200: PresignedUrlResponseSerializer},
)
class AnswerPresignedUrlView(PresignedUrlView):
    """presignedurl view"""

    permission_classes: list[type[Any]] = [IsStudentUser]
    path = "uploads/images/answers/"


class AnswerView(APIView):
    """
    POST api/v1/qna/questions/{question_id}/answers
    답변 등록 API
    """

    permission_classes = [IsStudentUser]
    service = AnswerService()

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if request.user.is_authenticated:
            raise PermissionDenied(detail="답변 작성 권한이 없습니다.")
        raise NotAuthenticated("로그인한 사용자만 답변을 작성할 수 있습니다.")

    @answer_create_schema
    def post(self, request: AuthenticatedRequest, question_id: int) -> Response:
        serializer = AnswerRequestSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
        try:
            question = self.service.get_question(question_id)
            answer = self.service.answer_create(
                question_id=question.id,
                user=request.user,
                **serializer.validated_data,
            )
        except BaseCustomException as e:
            return Response({"error_detail": str(e)}, status=e.status_code)
        return Response(AnswerResponseSerializer(answer).data, status=status.HTTP_201_CREATED)


class AnswerAcceptView(APIView):
    """
    POST /api/v1/qna/answers/{answer_id}/accept
    답변 채택에 관한 view
    """

    permission_classes = [IsStudentUser]
    service = AnswerAcceptService()

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if request.user.is_authenticated:
            raise PermissionDenied(detail="답변 채택 권한이 없습니다.")
        raise NotAuthenticated("로그인한 사용자만 답변을 채택할 수 있습니다.")

    @answer_accept_schema
    def post(self, request: AuthenticatedRequest, answer_id: int) -> Response:
        try:
            answer = self.service.answer_accept(
                user=request.user,
                answer_id=answer_id,
            )
        except BaseCustomException as e:
            return Response({"error_detail": str(e)}, status=e.status_code)
        return Response(AnswerAcceptResponseSerializer(answer).data, status=status.HTTP_200_OK)


class AnswerDetail(APIView):
    """
    PUT /api/v1/qna/answers/{answer_id}
    답변 수정 API
    """

    permission_classes = [IsStudentUser]
    answer_service = AnswerDetailService()

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if request.user.is_authenticated:
            raise PermissionDenied(detail="답변 수정 권한이 없습니다.")
        raise NotAuthenticated("로그인한 사용자만 답변을 수정할 수 있습니다.")

    @answer_update_schema
    def put(self, request: AuthenticatedRequest, answer_id: int) -> Response:
        serializer = AnswerRequestSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
        try:
            answer = self.answer_service.get_answer(answer_id)
            updated_answer = self.answer_service.update(
                request.user,
                answer,
                **serializer.validated_data,
            )
        except BaseCustomException as e:
            return Response({"error_detail": str(e)}, status=e.status_code)
        return Response(AnswerUpdateSerializer(updated_answer).data, status=status.HTTP_200_OK)


class AnswerCommentView(APIView):
    """
    POST api/v1/qna/answers/{answer_id}/comments
    답변 댓글 작성 API
    """

    permission_classes = [IsStudentUser]
    answer_comment_service = AnswerCommentService()

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if request.user.is_authenticated:
            raise PermissionDenied(detail="댓글 작성 권한이 없습니다.")
        raise NotAuthenticated("로그인한 사용자만 댓글을 작성할 수 있습니다.")

    @answer_comment_schema
    def post(self, request: AuthenticatedRequest, answer_id: int) -> Response:
        serializer = AnswerCommentRequestSerializer(
            data=request.data,
        )
        if not serializer.is_valid():
            error = list(serializer.errors.values())[0][0]
            raise ValidationError(detail=error)
        try:
            answer = self.answer_comment_service.get_object(answer_id)
            answer_comment = self.answer_comment_service.create_comment(
                answer_id=answer.id,
                user=request.user,
                **serializer.validated_data,
            )
        except BaseCustomException as e:
            return Response({"error_detail": str(e)}, status=e.status_code)
        return Response(AnswerCommentResponseSerializer(answer_comment).data, status=status.HTTP_201_CREATED)

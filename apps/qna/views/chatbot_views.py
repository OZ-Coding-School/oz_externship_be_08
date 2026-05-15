import json
from typing import Any, Callable, Iterator, NoReturn

from django.http import StreamingHttpResponse
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.types import AuthenticatedRequest
from apps.qna.dtos import InitialQNA, Message
from apps.qna.exceptions import BaseCustomException
from apps.qna.redis import CacheRepository
from apps.qna.schemas.chatbot_schemas import (
    ai_answer_get_schema,
    ai_answer_post_schema,
    cs_chatbot_get_schema,
    cs_chatbot_post_schema,
    qna_chatbot_get_schema,
    qna_chatbot_list_schema,
    qna_chatbot_post_schema,
)
from apps.qna.serializers.chatbot_serializers import (
    ChatbotRequestSerializer,
    HistoryResponseSerializer,
    InitialAIAnswerSerializer,
    QNAChatbotListResponseSerializer,
)
from apps.qna.services.chatbot_cs import CSChatbotService
from apps.qna.services.chatbot_initial_qna import InitialService
from apps.qna.services.chatbot_qna import QNAChatbotService


class InitialAiAnswerAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user.is_authenticated:
            raise NotAuthenticated("로그인한 사용자만 요청할 수 있습니다.")
        raise PermissionDenied(message)

    @ai_answer_get_schema
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            instance = InitialService.get_initial_answer(kwargs["question_id"])
            serializer = InitialAIAnswerSerializer(instance=instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BaseCustomException as e:
            return Response({"error_detail": str(e)}, status=e.status_code)

    @ai_answer_post_schema
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            instance = InitialService.save_initial_answer(kwargs["question_id"])
            serializer = InitialAIAnswerSerializer(instance=instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except BaseCustomException as e:
            return Response({"error_detail": str(e)}, status=e.status_code)
        except Exception:
            return Response(
                {"error_detail": "서버 내부 오류가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QNAChatbotAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user.is_authenticated:
            raise NotAuthenticated("로그인한 사용자만 요청할 수 있습니다.")
        raise PermissionDenied(message)

    @qna_chatbot_get_schema
    def get(self, request: AuthenticatedRequest, *args: Any, **kwargs: Any) -> Response:
        try:
            history = QNAChatbotService.response_qna_history(request.user.id, kwargs["question_id"])
            serializer = HistoryResponseSerializer(history, many=True)
            return Response({"results": serializer.data}, status=status.HTTP_200_OK)
        except BaseCustomException as e:
            return Response({"error_detail": str(e)}, status=e.status_code)

    @qna_chatbot_post_schema
    def post(self, request: AuthenticatedRequest, *args: Any, **kwargs: Any) -> Response | StreamingHttpResponse:
        serializer = ChatbotRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            ctx = QNAChatbotService.make_qna_context(request.user.id, kwargs["question_id"])
            return StreamingHttpResponse(
                self._build_qna_stream(
                    initial=ctx.initial, history=ctx.history, key=ctx.key, message=serializer.validated_data["message"]
                ),
                content_type="text/event-stream",
            )
        except BaseCustomException as e:
            return Response({"error_detail": str(e)}, status=e.status_code)

    @staticmethod
    def _build_qna_stream(initial: InitialQNA, history: list[Message] | None, key: str, message: str) -> Iterator[str]:
        try:
            for chunk in QNAChatbotService.response_qna_chat(initial, history, key, message):
                yield f'data: {json.dumps({"message": chunk}, ensure_ascii=False)}\n\n'
        except BaseCustomException as e:
            yield f'data: {json.dumps({"error_detail": str(e)}, ensure_ascii=False)}\n\n'
        yield "data: [DONE]\n\n"


class QNAChatbotListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user.is_authenticated:
            raise NotAuthenticated("로그인한 사용자만 요청할 수 있습니다.")
        raise PermissionDenied(message)

    @qna_chatbot_list_schema
    def get(self, request: AuthenticatedRequest, *args: Any, **kwargs: Any) -> Response:
        instance = QNAChatbotService.response_qna_list(request.user.pk)
        serializer = QNAChatbotListResponseSerializer(instance, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)


class CSChatbotAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user.is_authenticated:
            raise NotAuthenticated("로그인한 사용자만 요청할 수 있습니다.")
        raise PermissionDenied(message)

    @cs_chatbot_get_schema
    def get(self, request: AuthenticatedRequest, *args: Any, **kwargs: Any) -> Response:
        history = CSChatbotService.response_cs_history(request.user.id)
        serializer = HistoryResponseSerializer(history, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)

    @cs_chatbot_post_schema
    def post(self, request: AuthenticatedRequest, *args: Any, **kwargs: Any) -> Response | StreamingHttpResponse:
        serializer = ChatbotRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        generator = CSChatbotService.response_cs_chat(
            user_id=request.user.id, message=serializer.validated_data["message"]
        )
        try:
            first = next(generator)
        except BaseCustomException as e:
            return Response({"error_detail": str(e)}, status=e.status_code)

        return StreamingHttpResponse(
            self._build_cs_stream(
                generator=generator,
                first=first,
            ),
            content_type="text/event-stream",
        )

    @staticmethod
    def _build_cs_stream(generator: Iterator[str], first: str) -> Iterator[str]:
        yield f'data: {json.dumps({"message": first}, ensure_ascii=False)}\n\n'
        try:
            for chunk in generator:
                yield f'data: {json.dumps({"message": chunk}, ensure_ascii=False)}\n\n'
        except BaseCustomException as e:
            yield f'data: {json.dumps({"error_detail": str(e)}, ensure_ascii=False)}\n\n'
        yield "data: [DONE]\n\n"

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.qna.models.question_models import Questions
from apps.qna.serializers.answer_serializers import (
    AnswerRequestSerializer,
    AnswerResponseSerializer,
)
from apps.qna.services.answer_services import answer_create


class AnswerView(APIView):
    permission_classes = [IsAuthenticated]
    # TODO: 유저에서 staff 로그인에 관한 permission 구현 후 permission_classes 추가 -> 403

    def post(self, request: Request, question_id: int) -> Response:
        question = get_object_or_404(Questions, pk=question_id)
        serializer = AnswerRequestSerializer(
            data=request.data,
        )
        if not serializer.is_valid():
            return Response({"error_detail": "유효하지 않은 답변 등록 요청입니다."},
                            status=status.HTTP_400_BAD_REQUEST)

        author_id = request.user.id
        assert author_id is not None

        answer = answer_create(
            content=serializer.validated_data["content"],
            img_urls=serializer.validated_data["img_urls"],
            question_id=question.id,
            author_id=author_id,
        )
        return Response(AnswerResponseSerializer(answer).data, status=status.HTTP_201_CREATED)

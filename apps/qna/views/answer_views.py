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

# Create your views here.


class AnswerView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request: Request, question_id:int)->Response:
        question = get_object_or_404(Questions, pk=question_id)
        serializer = AnswerRequestSerializer(
            data=request.data,
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        answer = serializer.create(
            {
                **serializer.validated_data,
                "question_id": question.id,
                "author_id": request.user.id,
            }
        )
        return Response(AnswerResponseSerializer(answer).data, status=status.HTTP_201_CREATED)

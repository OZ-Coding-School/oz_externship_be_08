from typing import NoReturn

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsStudentUser
from apps.exams.exceptions.exam_submission_exception import (
    DeploymentNotFound,
    SubmissionAlreadyExists,
    UserSubmissionNotFound,
)
from apps.exams.serializers.user_exam_submission_serializer import (
    UserExamSubmissionCreateResponseSerializer,
    UserExamSubmissionCreateSerializer,
    UserExamSubmissionExtendSchemaSerializer,
    UserExamSubmissionGetSerializer,
)
from apps.exams.services.user_exam_submission_service import (
    create_submission,
    get_submission_detail,
)


class UserExamSubmissionGetView(APIView):

    permission_classes = [IsStudentUser]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user.is_authenticated:
            raise NotAuthenticated("자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied("권한이 없습니다.")

    @extend_schema(
        tags=["user-exams"],
        summary="쪽지시험 결과 확인 API",
        responses={
            200: UserExamSubmissionExtendSchemaSerializer,
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="해당 시험 정보를 찾을 수 없습니다."),
        },
    )
    def get(self, request: Request, submission_id: int) -> Response:
        try:
            assert request.user.id is not None
            submission = get_submission_detail(submitter=request.user.id, submission_id=submission_id)
        except UserSubmissionNotFound as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserExamSubmissionGetSerializer(submission)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserExamSubmissionCreateView(APIView):
    permission_classes = [IsStudentUser]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user.is_authenticated:
            raise NotAuthenticated("자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied("권한이 없습니다.")

    @extend_schema(
        tags=["exams"],
        summary="쪽지시험 응시 제출 API",
        request=UserExamSubmissionCreateSerializer,
        responses={
            201: UserExamSubmissionCreateResponseSerializer,
            400: OpenApiResponse(description="유효하지 않은 시험 응시 세션입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="해당 시험 정보를 찾을 수 없습니다."),
            409: OpenApiResponse(description="이미 제출된 시험입니다."),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = UserExamSubmissionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error_detail": "유효하지 않은 시험 응시 세션입니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assert request.user.id is not None
            submission = create_submission(request.user.id, serializer.validated_data)
        except DeploymentNotFound as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except SubmissionAlreadyExists as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_409_CONFLICT)

        return Response(
            {
                "submission_id": submission.id,
                "score": submission.score,
                "correct_answer_count": submission.correct_answer_count,
                "redirect_url": f"/quiz/{submission.id}/result",
            },
            status=status.HTTP_201_CREATED,
        )

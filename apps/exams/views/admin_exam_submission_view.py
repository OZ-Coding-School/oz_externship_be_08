from typing import Never

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.pagination import PageNumberPagination as BasePageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsRoleAdminUser
from apps.exams.exceptions.admin_exam_submission_exception import (
    SubmissionConflictError,
    SubmissionDeleteNotFoundError,
    SubmissionNotFoundError,
)
from apps.exams.serializers.admin_exam_submission_serializer import (
    AdminExamSubmissionDetailSerializer,
    AdminExamSubmissionListQuerySerializer,
    AdminExamSubmissionListSerializer,
    AdminExamSubmissionPathSerializer,
)
from apps.exams.services.admin_exam_submission_service import (
    delete_submission,
    get_submission_detail,
    get_submission_list,
)


class ExamSubmissionPagination(BasePageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class AdminExamSubmissionView(APIView):
    permission_classes = [IsRoleAdminUser]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> Never:
        if request.authenticators and not request.successful_authenticator:
            raise NotAuthenticated("자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied("쪽지시험 응시 내역 조회 권한이 없습니다.")

    @extend_schema(
        tags=["admin-exams"],
        summary="쪽지시험 응시내역 목록 조회",
        parameters=[AdminExamSubmissionListQuerySerializer],
        responses={
            200: AdminExamSubmissionListSerializer,
            400: OpenApiResponse(description="유효하지 않은 조회 요청입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="쪽지시험 응시 내역 조회 권한이 없습니다."),
        },
    )
    def get(self, request: Request) -> Response:
        query_serializer = AdminExamSubmissionListQuerySerializer(data=request.query_params)
        if not query_serializer.is_valid():
            return Response({"error_detail": "유효하지 않은 조회 요청입니다."}, status=status.HTTP_400_BAD_REQUEST)

        submissions = get_submission_list(query_serializer.validated_data)

        paginator = ExamSubmissionPagination()
        paginated = paginator.paginate_queryset(submissions, request)

        serializer = AdminExamSubmissionListSerializer(paginated, many=True)
        return paginator.get_paginated_response(serializer.data)


class AdminExamSubmissionDetailView(APIView):
    permission_classes = [IsRoleAdminUser]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> Never:
        if request.authenticators and not request.successful_authenticator:
            raise NotAuthenticated("자격 인증 데이터가 제공되지 않았습니다.")
        if request.method == "GET":
            raise PermissionDenied("쪽지시험 응시 상세 조회 권한이 없습니다.")
        if request.method == "DELETE":
            raise PermissionDenied("쪽지시험 응시 내역 삭제 권한이 없습니다.")
        raise PermissionDenied("권한이 없습니다.")

    @extend_schema(
        tags=["admin-exams"],
        summary="쪽지시험 응시내역 상세 조회",
        responses={
            200: AdminExamSubmissionDetailSerializer,
            400: OpenApiResponse(description="유효하지 않은 상세 조회 요청입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="쪽지시험 응시 상세 조회 권한이 없습니다."),
            404: OpenApiResponse(description="해당 응시 내역을 찾을 수 없습니다."),
        },
    )
    def get(self, request: Request, submission_id: int) -> Response:
        path_serializer = AdminExamSubmissionPathSerializer(data={"submission_id": submission_id})
        if not path_serializer.is_valid():
            return Response({"error_detail": "유효하지 않은 상세 조회 요청입니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            submission = get_submission_detail(submission_id)
        except SubmissionNotFoundError as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminExamSubmissionDetailSerializer(submission)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["admin-exams"],
        summary="쪽지시험 응시내역 삭제",
        responses={
            200: OpenApiResponse(description="삭제된 응시내역 ID"),
            400: OpenApiResponse(description="유효하지 않은 응시 내역 삭제 요청입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="쪽지시험 응시 내역 삭제 권한이 없습니다."),
            404: OpenApiResponse(description="삭제할 응시 내역을 찾을 수 없습니다."),
            409: OpenApiResponse(description="응시 내역 삭제 처리 중 충돌이 발생했습니다."),
        },
    )
    def delete(self, request: Request, submission_id: int) -> Response:
        path_serializer = AdminExamSubmissionPathSerializer(data={"submission_id": submission_id})
        if not path_serializer.is_valid():
            return Response(
                {"error_detail": "유효하지 않은 응시 내역 삭제 요청입니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            delete_submission(submission_id)
        except SubmissionDeleteNotFoundError as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except SubmissionConflictError as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_409_CONFLICT)

        return Response({"submission_id": submission_id}, status=status.HTTP_200_OK)

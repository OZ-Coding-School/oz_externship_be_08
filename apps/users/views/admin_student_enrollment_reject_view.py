from __future__ import annotations

from typing import NoReturn

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsRoleAdminUser
from apps.users.serializers.admin_student_enrollment_reject_serializer import (
    AdminStudentEnrollmentErrorSerializer,
    AdminStudentEnrollmentRejectRequestSerializer,
    AdminStudentEnrollmentRejectResponseSerializer,
    AdminStudentEnrollmentValidationErrorSerializer,
)
from apps.users.services.admin_student_enrollment_reject_service import (
    reject_student_enrollments,
)


class AdminStudentEnrollmentRejectView(APIView):
    permission_classes = [IsRoleAdminUser]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user.is_authenticated:
            raise NotAuthenticated("자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied("권한이 없습니다.")

    @extend_schema(
        tags=["admin-students"],
        summary="어드민 수강생 등록 요청 거절",
        description="어드민이 수강생 등록 신청들에 대한 거절 요청을 처리합니다.",
        request=AdminStudentEnrollmentRejectRequestSerializer,
        responses={
            200: AdminStudentEnrollmentRejectResponseSerializer,
            400: OpenApiResponse(
                description="잘못된 요청",
                response=AdminStudentEnrollmentValidationErrorSerializer,
            ),
            401: OpenApiResponse(
                description="인증 실패",
                response=AdminStudentEnrollmentErrorSerializer,
            ),
            403: OpenApiResponse(
                description="권한 없음",
                response=AdminStudentEnrollmentErrorSerializer,
            ),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = AdminStudentEnrollmentRejectRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        reject_student_enrollments(serializer.validated_data["enrollments"])
        return Response(
            {"detail": "수강생 등록 신청들에 대한 거절 요청이 처리되었습니다."},
            status=status.HTTP_200_OK,
        )

from typing import NoReturn

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import exceptions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsRoleAdminUser
from apps.users.serializers.enrollment_accept_serializer import (
    AdminEnrollmentAcceptSerializer,
)
from apps.users.services.enrollment_accept_service import (
    AdminEnrollmentAcceptService,
    EnrollmentAcceptError,
)


class AdminStudentEnrollmentAcceptView(APIView):

    permission_classes = [IsRoleAdminUser]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if request.authenticators and not request.successful_authenticator:
            raise exceptions.NotAuthenticated("자격 인증 데이터가 제공되지 않았습니다.")
        raise exceptions.PermissionDenied("권한이 없습니다.")

    @extend_schema(
        tags=["admin-students"],
        summary="수강생 등록 요청 승인",
        description="어드민 페이지 수강생 등록 요청 승인 API",
        request=AdminEnrollmentAcceptSerializer,
        responses={
            200: OpenApiResponse(description="수강생 등록 신청들에 대한 승인 요청이 처리되었습니다."),
            400: OpenApiResponse(description="이 필드는 필수 항목입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = AdminEnrollmentAcceptSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            AdminEnrollmentAcceptService.accept_enrollments(serializer.validated_data["enrollments"])
        except EnrollmentAcceptError as exc:
            return Response(
                {"error_detail": f"처리할 수 없는 등록 요청 ID가 포함되어 있습니다: {exc.invalid_ids}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "수강생 등록 신청들에 대한 승인 요청이 처리되었습니다."},
            status=status.HTTP_200_OK,
        )

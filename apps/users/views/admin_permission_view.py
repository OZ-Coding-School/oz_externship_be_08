from typing import Never

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import (
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsRoleAdminUser
from apps.users.serializers.admin_permission_serializer import AdminPermissionSerializer
from apps.users.services.admin_permission_service import update_user_role
from apps.users.utils.user_exceptions import UserNotFoundError


class AdminPermissionView(APIView):
    permission_classes = [IsRoleAdminUser]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> Never:
        if not request.user.is_authenticated:
            raise NotAuthenticated("자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied("권한이 없습니다.")

    @extend_schema(
        tags=["admin-accounts"],
        summary="어드민 페이지 권한 변경 API",
        description="관리자 권한을 가진 유저는 특정 유저 권한 변경 가능",
        request=AdminPermissionSerializer,
        responses={
            200: OpenApiResponse(description="권한이 변경되었습니다."),
            400: OpenApiResponse(description="role로 권한 변경 시 필수 필드입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="사용자 정보를 찾을 수 없습니다."),
        },
    )
    def patch(self, request: Request, account_id: int) -> Response:
        serializer = AdminPermissionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            update_user_role(account_id, serializer.validated_data)
        except UserNotFoundError as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "권한이 변경되었습니다."}, status=status.HTTP_200_OK)

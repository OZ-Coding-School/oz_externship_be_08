from typing import Never

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsRoleAdminUser
from apps.users.serializers.admin_student_list_serializer import (
    AdminStudentListSerializer,
)
from apps.users.services.admin_student_list_service import get_student_list


class AdminStudentListView(APIView):
    permission_classes = [IsRoleAdminUser]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> Never:
        if not request.user.is_authenticated:
            raise NotAuthenticated("자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied("권한이 없습니다.")

    @extend_schema(
        tags=["admin-students"],
        summary="어드민 페이지 수강생 목록 조회 API",
        description="관리자 권한을 가진 유저는 어드민 페이지 회원관리메뉴에서 등록된 수강생 목록 조회 가능",
        parameters=[
            OpenApiParameter(name="page", type=int, required=False),
            OpenApiParameter(name="page_size", type=int, required=False),
            OpenApiParameter(name="search", type=str, required=False),
            OpenApiParameter(name="status", type=str, required=False, enum=["ACTIVATED", "DEACTIVATED", "WITHDREW"]),
        ],
        responses={
            200: AdminStudentListSerializer(many=True),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
        },
    )
    def get(self, request: Request) -> Response:
        page, paginator = get_student_list(request)
        serializer = AdminStudentListSerializer(page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        return Response(response.data, status=status.HTTP_200_OK)

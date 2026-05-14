from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsRoleAdminUser
from apps.users.models import StudentEnrollmentRequests
from apps.users.serializers.admin_student_enrollment_serializer import (
    StudentEnrollmentListSerializer,
)
from apps.users.services.admin_student_enrollment_service import get_enrollment_requests
from apps.users.utils.pagination import RequestPagination


class AdminEnrollmentRequestListView(APIView):
    permission_classes = [IsRoleAdminUser]

    @extend_schema(
        tags=["admin-students"],
        summary="수강생 등록 신청 목록 조회",
        description="어드민 페이지에서 수강생 등록 신청 목록을 조회합니다. (ADMIN 권한 필요)",
        parameters=[
            OpenApiParameter(name="page", type=int, required=False, default=1, description="페이지 번호"),
            OpenApiParameter(
                name="page_size", type=int, required=False, default=10, description="페이지당 항목 수 (최대 100)"
            ),
            OpenApiParameter(name="search", type=str, required=False, description="이름 또는 이메일 검색"),
            OpenApiParameter(
                name="status",
                type=str,
                required=False,
                enum=["pending", "accepted", "rejected", "canceled"],
                description="요청 처리 상태 필터",
            ),
            OpenApiParameter(
                name="sort",
                type=str,
                required=False,
                default="id_asc",
                enum=["id_asc", "latest", "oldest"],
                description="정렬 기준",
            ),
        ],
        responses={
            status.HTTP_200_OK: StudentEnrollmentListSerializer(many=True),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="잘못된 요청"),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description="인증 실패"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="권한 없음"),
        },
    )
    def get(self, request: Request) -> Response:
        # 쿼리 파라미터 파싱 및 검증
        status_param = request.query_params.get("status")

        if status_param:
            if status_param not in StudentEnrollmentRequests.Status.values:
                return Response({"error_detail": "유효하지 않은 상태값입니다."}, status=status.HTTP_400_BAD_REQUEST)

        search = request.query_params.get("search")
        sort = request.query_params.get("sort", "id_asc")

        #  전체 QuerySet
        queryset = get_enrollment_requests(status=status_param, search=search, sort=sort)

        # Pagination 객체 생성 및 적용
        paginator = RequestPagination()
        # 클라이언트가 요청한 page 번호에 맞게 전체 queryset을 page_size 자르기
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)

        # 직렬화(Serialization)
        serializer = StudentEnrollmentListSerializer(paginated_queryset, many=True)

        # 최종 응답 반환 (count, next, previous 메타 데이터를 포함하여 응답)
        return paginator.get_paginated_response(serializer.data)

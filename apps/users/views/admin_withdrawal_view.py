from __future__ import annotations

from typing import NoReturn

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsRoleAdminUser
from apps.users.serializers.admin_withdrawal_serializer import (
    ErrorDetailSerializer,
    ValidationErrorDetailSerializer,
    WithdrawalCancelResponseSerializer,
    WithdrawalDetailSerializer,
    WithdrawalListQuerySerializer,
    WithdrawalListResponseSerializer,
    WithdrawalListSerializer,
)
from apps.users.services.admin_withdrawal_service import (
    AdminWithdrawalNotFoundError,
    cancel_withdrawal,
    get_withdrawal_detail,
    get_withdrawal_list,
)


class AdminWithdrawalPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 100


class AdminWithdrawalListView(APIView):
    permission_classes = [IsRoleAdminUser]
    serializer_class = WithdrawalListSerializer

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        # 명세서의 401/403 메시지를 맞추기 위해 DRF 기본 권한 에러를 구분해서 반환한다.
        if not request.user.is_authenticated:
            raise NotAuthenticated("자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied("권한이 없습니다.")

    @extend_schema(
        tags=["admin-withdrawals"],
        summary="어드민 회원 탈퇴 내역 목록 조회",
        description="어드민이 회원 탈퇴 내역을 페이지네이션, 검색, 역할, 정렬 조건으로 조회합니다.",
        parameters=[WithdrawalListQuerySerializer],
        responses={
            200: WithdrawalListResponseSerializer,
            400: OpenApiResponse(
                description="잘못된 쿼리 파라미터",
                response=ValidationErrorDetailSerializer,
            ),
            401: OpenApiResponse(
                description="인증 실패",
                response=ErrorDetailSerializer,
            ),
            403: OpenApiResponse(
                description="권한 없음",
                response=ErrorDetailSerializer,
            ),
        },
    )
    def get(self, request: Request) -> Response:
        query_serializer = WithdrawalListQuerySerializer(data=request.query_params)
        if not query_serializer.is_valid():
            return Response({"error_detail": query_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        queryset = get_withdrawal_list(
            search=query_serializer.validated_data.get("search"),
            role=query_serializer.validated_data.get("role"),
            position=query_serializer.validated_data.get("position"),
            sort=query_serializer.validated_data.get("sort"),
        )
        paginator = AdminWithdrawalPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = WithdrawalListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class AdminWithdrawalDetailView(APIView):
    permission_classes = [IsRoleAdminUser]
    serializer_class = WithdrawalDetailSerializer

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        # 명세서의 401/403 메시지를 맞추기 위해 DRF 기본 권한 에러를 구분해서 반환한다.
        if not request.user.is_authenticated:
            raise NotAuthenticated("자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied("권한이 없습니다.")

    @extend_schema(
        tags=["admin-withdrawals"],
        summary="어드민 회원 탈퇴 내역 상세 조회",
        description="어드민이 특정 회원 탈퇴 내역을 상세 조회합니다.",
        responses={
            200: WithdrawalDetailSerializer,
            401: OpenApiResponse(
                description="인증 실패",
                response=ErrorDetailSerializer,
            ),
            403: OpenApiResponse(
                description="권한 없음",
                response=ErrorDetailSerializer,
            ),
            404: OpenApiResponse(
                description="회원탈퇴 정보를 찾을 수 없습니다.",
                response=ErrorDetailSerializer,
            ),
        },
    )
    def get(self, request: Request, withdrawal_id: int) -> Response:
        try:
            withdrawal = get_withdrawal_detail(withdrawal_id)
        except AdminWithdrawalNotFoundError as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = WithdrawalDetailSerializer(withdrawal)
        return Response(serializer.data)

    @extend_schema(
        tags=["admin-withdrawals"],
        summary="어드민 회원 탈퇴 취소",
        description="어드민이 특정 회원 탈퇴 신청을 취소합니다.",
        responses={
            200: WithdrawalCancelResponseSerializer,
            401: OpenApiResponse(
                description="인증 실패",
                response=ErrorDetailSerializer,
            ),
            403: OpenApiResponse(
                description="권한 없음",
                response=ErrorDetailSerializer,
            ),
            404: OpenApiResponse(
                description="회원탈퇴 정보를 찾을 수 없습니다.",
                response=ErrorDetailSerializer,
            ),
        },
    )
    def delete(self, request: Request, withdrawal_id: int) -> Response:
        try:
            cancel_withdrawal(withdrawal_id)
        except AdminWithdrawalNotFoundError as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "회원 탈퇴 취소처리 완료."})

from typing import Never

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import exceptions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.presigned_url.serializers import (
    PresignedUrlRequestSerializer,
    PresignedUrlResponseSerializer,
)
from apps.core.utils.permissions import IsRoleAdminUser
from apps.core.utils.s3 import PresignedUrlView
from apps.courses.serializers.subject_serializer import (
    SubjectCreateSerializer,
    SubjectDetailSerializer,
    SubjectListSerializer,
    SubjectUpdateSerializer,
)
from apps.courses.services import subject_service
from apps.courses.utils.exceptions import SubjectBadRequestError


class SubjectListView(APIView):
    permission_classes = [IsRoleAdminUser]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> Never:
        if not request.successful_authenticator:
            raise exceptions.NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.", code=code)
        raise exceptions.PermissionDenied(detail="이 리소스를 조회할 권한이 없습니다.", code=code)

    @extend_schema(
        tags=["admin-subject"],
        summary="어드민 과목 목록 조회",
        responses={
            200: SubjectListSerializer(many=True),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="이 리소스를 조회할 권한이 없습니다."),
        },
    )
    def get(self, request: Request, course_id: int) -> Response:
        subjects = subject_service.get_subject_list(course_id=course_id)
        return Response(SubjectListSerializer(subjects, many=True).data, status=status.HTTP_200_OK)


class SubjectCreateView(APIView):
    permission_classes = [IsRoleAdminUser]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> Never:
        if not request.successful_authenticator:
            raise exceptions.NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.", code=code)
        raise exceptions.PermissionDenied(detail="과목 생성 권한이 없습니다.", code=code)

    @extend_schema(
        tags=["admin-subject"],
        summary="어드민 과목 생성",
        request=SubjectCreateSerializer,
        responses={
            200: SubjectCreateSerializer,
            400: OpenApiResponse(description="유효하지 않은 과목 생성입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="과목 생성 권한이 없습니다."),
            404: OpenApiResponse(description="해당 과정을 찾을 수 없습니다."),
            409: OpenApiResponse(description="동일한 이름의 과목이 이미 존재합니다."),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = SubjectCreateSerializer(data=request.data)
        if not serializer.is_valid():
            raise SubjectBadRequestError()
        subject = subject_service.create_subject(**serializer.validated_data)
        return Response(SubjectCreateSerializer(subject).data, status=status.HTTP_200_OK)


class SubjectDetailView(APIView):
    permission_classes = [IsRoleAdminUser]

    _401_messages = {
        "GET": "로그인이 필요합니다.",
        "PATCH": "자격 인증 데이터가 제공되지 않았습니다.",
        "DELETE": "자격 인증 데이터가 제공되지 않았습니다.",
    }

    _403_messages = {
        "GET": "관리자 권한이 필요합니다.",
        "PATCH": "이 리소스를 수정할 권한이 없습니다.",
        "DELETE": "이 리소스를 삭제할 권한이 없습니다.",
    }

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> Never:
        if not request.successful_authenticator:
            raise exceptions.NotAuthenticated(
                detail=self._401_messages.get(request.method or "", "자격 인증 데이터가 제공되지 않았습니다."),
                code=code,
            )
        raise exceptions.PermissionDenied(
            detail=self._403_messages.get(request.method or "", "권한이 없습니다."), code=code
        )

    @extend_schema(
        tags=["admin-subject"],
        summary="어드민 과목 상세 조회",
        responses={
            200: SubjectDetailSerializer,
            401: OpenApiResponse(description="로그인이 필요합니다."),
            403: OpenApiResponse(description="관리자 권한이 필요합니다."),
            404: OpenApiResponse(description="해당 과목을 찾을 수 없습니다."),
        },
    )
    def get(self, request: Request, subject_id: int) -> Response:
        subject = subject_service.get_subject_detail(subject_id=subject_id)
        return Response(SubjectDetailSerializer(subject).data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["admin-subject"],
        summary="어드민 과목 수정",
        request=SubjectUpdateSerializer,
        responses={
            200: SubjectUpdateSerializer,
            400: OpenApiResponse(description="유효하지 않은 데이터입니다."),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="이 리소스를 수정할 권한이 없습니다."),
            404: OpenApiResponse(description="과목을 찾을 수 없습니다."),
        },
    )
    def patch(self, request: Request, subject_id: int) -> Response:
        subject = subject_service.get_subject_detail(subject_id=subject_id)
        serializer = SubjectUpdateSerializer(instance=subject, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({"error_detail": "유효하지 않은 데이터입니다."}, status=status.HTTP_400_BAD_REQUEST)
        subject = subject_service.update_subject(subject, **serializer.validated_data)
        return Response(SubjectUpdateSerializer(subject).data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["admin-subject"],
        summary="어드민 과목 삭제",
        responses={
            204: OpenApiResponse(description="No Content"),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="이 리소스를 삭제할 권한이 없습니다."),
            404: OpenApiResponse(description="과목을 찾을 수 없습니다."),
        },
    )
    def delete(self, request: Request, subject_id: int) -> Response:
        subject_service.delete_subject(subject_id=subject_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=["admin-subject"],
    summary="과목 이미지 presigned URL 발급",
    request=PresignedUrlRequestSerializer,
    responses={200: PresignedUrlResponseSerializer},
)
class SubjectPresignedUrlView(PresignedUrlView):
    permission_classes = [IsRoleAdminUser]
    path = "uploads/images/subjects/"

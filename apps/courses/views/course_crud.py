from typing import Any, NoReturn

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsRoleAdminUser
from apps.courses.serializers.course_crud import (
    CourseCreateRequestSerializer,
    CourseCreateResponseSerializer,
    CourseDeleteResponseSerializer,
    CourseDetailResponseSerializer,
    CourseListResponseSerializer,
    CourseUpdateRequestSerializer,
    CourseUpdateResponseSerializer,
    ErrorResponseSerializer,
    ValidationErrorResponseSerializer,
)
from apps.courses.services import course_crud as coursecrud_service
from apps.courses.utils.exceptions import (
    CourseAlreadyExistsError,
    CourseNotFoundError,
)


class AdminBaseView(APIView):
    permission_classes = [IsRoleAdminUser]

    def permission_denied(
        self,
        request: Request,
        message: Any = None,
        code: Any = None,
    ) -> NoReturn:
        # 401: 미인증
        if not request.user.is_authenticated:
            raise NotAuthenticated("자격 인증 데이터가 제공되지 않았습니다.")
        # 403: 권한 없음
        raise PermissionDenied("관리자 권한이 필요합니다.")


class CourseListView(AdminBaseView):
    @extend_schema(
        tags=["courses"],
        summary="과정 리스트 조회",
        responses={
            200: CourseListResponseSerializer(many=True),
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        courses = coursecrud_service.get_course_list()
        return Response(
            CourseListResponseSerializer(courses, many=True).data,
            status=status.HTTP_200_OK,
        )


class AdminCourseCreateView(AdminBaseView):
    @extend_schema(
        tags=["admin-courses"],
        summary="어드민 페이지 과정 등록",
        request=CourseCreateRequestSerializer,
        responses={
            201: CourseCreateResponseSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            409: ErrorResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        serializer = CourseCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            course = coursecrud_service.create_course(serializer.validated_data)
        except CourseAlreadyExistsError as e:
            return Response(
                {"error_detail": str(e)},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            CourseCreateResponseSerializer({"detail": "코스가 성공적으로 등록되었습니다.", "id": course.id}).data,
            status=status.HTTP_201_CREATED,
        )


class AdminCourseDetailView(AdminBaseView):
    def permission_denied(
        self,
        request: Request,
        message: Any = None,
        code: Any = None,
    ) -> NoReturn:
        if not request.user.is_authenticated:
            if request.method == "GET":
                raise NotAuthenticated("로그인이 필요합니다.")
            raise NotAuthenticated("자격 인증 데이터가 제공되지 않았습니다.")
        if request.method == "GET":
            raise PermissionDenied("관리자 권한이 필요합니다.")
        raise PermissionDenied("권한이 없습니다.")

    @extend_schema(
        tags=["admin-courses"],
        summary="어드민 페이지 과정 상세 조회",
        responses={
            200: CourseDetailResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def get(self, request: Request, course_id: int) -> Response:
        try:
            course = coursecrud_service.get_course_detail(course_id)
        except CourseNotFoundError:
            return Response(
                {"error_detail": "해당 과정을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            CourseDetailResponseSerializer(course).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["admin-courses"],
        summary="어드민 페이지 과정 정보 수정",
        request=CourseUpdateRequestSerializer,
        responses={
            200: CourseUpdateResponseSerializer,
            400: ValidationErrorResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def patch(self, request: Request, course_id: int) -> Response:
        serializer = CourseUpdateRequestSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            course = coursecrud_service.update_course(
                course_id=course_id,
                validated_data=serializer.validated_data,
            )
        except CourseNotFoundError as e:
            return Response(
                {"error_detail": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            CourseUpdateResponseSerializer(course).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["admin-courses"],
        summary="어드민 페이지 과정 삭제",
        responses={
            200: CourseDeleteResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def delete(self, request: Request, course_id: int) -> Response:
        try:
            coursecrud_service.delete_course(course_id)
        except CourseNotFoundError as e:
            return Response(
                {"error_detail": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            CourseDeleteResponseSerializer({"detail": "과정이 삭제되었습니다."}).data,
            status=status.HTTP_200_OK,
        )

from typing import Any, Never, cast

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import exceptions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsRoleAdminUser
from apps.courses.serializers.course_cohorts_serializer import (
    CohortAvgScoreSerializer,
    CohortCreateResponseSerializer,
    CohortCreateSerializer,
    CohortDetailSerializer,
    CohortListSerializer,
    CohortStudentSerializer,
    CohortUpdateResponseSerializer,
    CohortUpdateSerializer,
)
from apps.courses.services import course_cohorts_service


class CohortCreateView(APIView):
    permission_classes = [IsRoleAdminUser]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> Never:
        if not request.successful_authenticator:
            raise exceptions.NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.", code=code)
        raise exceptions.PermissionDenied(detail="권한이 없습니다.", code=code)

    @extend_schema(
        tags=["admin-cohort"],
        summary="어드민 페이지 기수 등록",
        request=CohortCreateSerializer,
        responses={
            201: CohortCreateResponseSerializer,
            400: OpenApiResponse(description="Bad Request"),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = CohortCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cohort = course_cohorts_service.create_cohort(serializer.validated_data)
        response_serializer = CohortCreateResponseSerializer({"id": cohort.id})

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CourseCohortListView(APIView):
    permission_classes = [IsAuthenticated]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> Never:
        if not request.successful_authenticator:
            raise exceptions.NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.", code=code)
        raise exceptions.PermissionDenied(detail="이 리소스를 조회할 권한이 없습니다.", code=code)

    @extend_schema(
        tags=["cohort"],
        summary="기수 리스트 조회",
        responses={
            200: CohortListSerializer(many=True),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="이 리소스를 조회할 권한이 없습니다."),
        },
    )
    def get(self, request: Request, course_id: int) -> Response:
        cohorts = course_cohorts_service.get_cohorts_by_course(course_id)
        serializer = CohortListSerializer(cohorts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CohortDetailView(APIView):
    permission_classes = [IsRoleAdminUser]

    _401_messages = {
        "GET": "로그인이 필요합니다.",
        "PATCH": "자격 인증 데이터가 제공되지 않았습니다.",
    }
    _403_messages = {
        "GET": "관리자 권한이 필요합니다.",
        "PATCH": "권한이 없습니다.",
    }

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> Never:
        if not request.successful_authenticator:
            raise exceptions.NotAuthenticated(
                detail=self._401_messages.get(request.method or "", "자격 인증 데이터가 제공되지 않았습니다."),
                code=code,
            )
        raise exceptions.PermissionDenied(
            detail=self._403_messages.get(request.method or "", "권한이 없습니다."),
            code=code,
        )

    @extend_schema(
        tags=["admin-cohort"],
        summary="어드민 페이지 기수 상세 조회",
        responses={
            200: CohortDetailSerializer,
            401: OpenApiResponse(description="로그인이 필요합니다."),
            403: OpenApiResponse(description="관리자 권한이 필요합니다."),
            404: OpenApiResponse(description="해당 기수를 찾을 수 없습니다."),
        },
    )
    def get(self, request: Request, cohort_id: int) -> Response:
        cohort = course_cohorts_service.get_cohort(
            cohort_id,
            not_found_message="해당 기수를 찾을 수 없습니다.",
        )
        serializer = CohortDetailSerializer(cohort)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["admin-cohort"],
        summary="어드민 페이지 기수 정보 수정",
        request=CohortUpdateSerializer,
        responses={
            200: CohortUpdateResponseSerializer,
            400: OpenApiResponse(description="Bad Request"),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="기수를 찾을 수 없습니다."),
        },
    )
    def patch(self, request: Request, cohort_id: int) -> Response:
        cohort = course_cohorts_service.get_cohort(cohort_id)

        serializer = CohortUpdateSerializer(cohort, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_cohort = course_cohorts_service.update_cohort(cohort, serializer.validated_data)
        response_serializer = CohortUpdateResponseSerializer(updated_cohort)

        return Response(response_serializer.data, status=status.HTTP_200_OK)


class CohortAvgScoreView(APIView):
    permission_classes = [IsRoleAdminUser]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> Never:
        if not request.successful_authenticator:
            raise exceptions.NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.", code=code)
        raise exceptions.PermissionDenied(detail="권한이 없습니다.", code=code)

    @extend_schema(
        tags=["admin-cohort"],
        summary="어드민 기수별 평균 점수 조회",
        responses={
            200: CohortAvgScoreSerializer(many=True),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="과정을 찾을 수 없습니다."),
        },
    )
    def get(self, request: Request, course_id: int) -> Response:
        avg_scores = course_cohorts_service.get_cohort_avg_scores(course_id)
        serializer = CohortAvgScoreSerializer(cast(Any, avg_scores), many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CohortStudentListView(APIView):
    permission_classes = [IsRoleAdminUser]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> Never:
        if not request.successful_authenticator:
            raise exceptions.NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.", code=code)
        raise exceptions.PermissionDenied(detail="권한이 없습니다.", code=code)

    @extend_schema(
        tags=["admin-cohort"],
        summary="어드민 기수별 수강생 목록 조회",
        responses={
            200: CohortStudentSerializer(many=True),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="기수를 찾을 수 없습니다."),
        },
    )
    def get(self, request: Request, cohort_id: int) -> Response:
        students = course_cohorts_service.get_cohort_students(cohort_id)
        serializer = CohortStudentSerializer(students, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from apps.courses.models.cohort import Cohort
from apps.courses.models.course import Course
from apps.users.models import StudentEnrollmentRequests, User
from apps.users.views.admin_student_enrollment_reject_view import (
    AdminStudentEnrollmentRejectView,
)


def create_user(
    email: str = "test@oz.com",
    password: str = "Test1234!@",
    nickname: str = "테스터",
    name: str = "홍길동",
    phone_number: str = "01012345678",
    role: str = User.Role.USER,
) -> User:
    return User.objects.create_user(
        email=email,
        password=password,
        nickname=nickname,
        name=name,
        phone_number=phone_number,
        role=role,
    )


def create_admin() -> User:
    return create_user(
        email="admin@oz.com",
        nickname="관리자",
        phone_number="01099998888",
        role=User.Role.ADMIN,
    )


def create_cohort() -> Cohort:
    course = Course.objects.create(name="초격차 백엔드 부트캠프", tag="BE")
    return Cohort.objects.create(
        course=course,
        number=1,
        max_student=30,
        start_date=timezone.localdate(),
        end_date=timezone.localdate() + timedelta(weeks=24),
    )


class AdminStudentEnrollmentRejectViewTest(APITestCase):
    """POST /api/v1/admin/student-enrollments/reject 수강생 등록 요청 거절"""

    def setUp(self) -> None:
        self.admin = create_admin()
        self.factory = APIRequestFactory()
        self.view = AdminStudentEnrollmentRejectView.as_view()
        self.url = "/api/v1/admin/student-enrollments/reject"
        self.cohort = create_cohort()
        self.user = create_user(email="student@oz.com", nickname="수강생", phone_number="01022223333")
        self.enrollment = StudentEnrollmentRequests.objects.create(
            user=self.user,
            cohort=self.cohort,
            status=StudentEnrollmentRequests.Status.PENDING,
        )

    def post_reject(self, data: dict[str, Any], user: User | None = None) -> Response:
        request = self.factory.post(self.url, data=data, format="json")
        if user is not None:
            force_authenticate(request, user=user)
        return self.view(request)

    def test_admin_can_reject_student_enrollments(self) -> None:
        response = self.post_reject({"enrollments": [self.enrollment.id]}, self.admin)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "수강생 등록 신청들에 대한 거절 요청이 처리되었습니다.")
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.status, StudentEnrollmentRequests.Status.REJECTED)

    def test_missing_enrollments_returns_400_with_exact_message(self) -> None:
        response = self.post_reject({}, self.admin)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {"error_detail": {"enrollments": ["이 필드는 필수 항목입니다."]}},
        )

    def test_without_token_returns_401_with_exact_message(self) -> None:
        response = self.post_reject({"enrollments": [self.enrollment.id]})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {"error_detail": "자격 인증 데이터가 제공되지 않았습니다."})

    def test_non_admin_returns_403_with_exact_message(self) -> None:
        normal_user = create_user(email="normal@oz.com", nickname="일반유저", phone_number="01033334444")

        response = self.post_reject({"enrollments": [self.enrollment.id]}, normal_user)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {"error_detail": "권한이 없습니다."})

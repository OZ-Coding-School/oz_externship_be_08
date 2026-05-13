# apps/users/tests/test_admin_permission_view.py
from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.courses.models.cohort import Cohort
from apps.courses.models.course import Course
from apps.users.models import (
    CohortStudents,
    LearningCoachs,
    OperationManagers,
    TrainigAssistants,
    User,
)


class AdminPermissionViewTest(APITestCase):
    admin_user: User
    target_user: User
    course: Course
    cohort: Cohort

    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="Test1234!",
            name="어드민",
            nickname="어드민닉",
            phone_number="01011112222",
            role=User.Role.ADMIN,
        )
        cls.target_user = User.objects.create_user(
            email="target@test.com",
            password="Test1234!",
            name="대상유저",
            nickname="대상닉",
            phone_number="01033334444",
            role=User.Role.USER,
        )
        cls.course = Course.objects.create(name="백엔드", tag="BE")
        cls.cohort = Cohort.objects.create(
            course=cls.course,
            number=1,
            max_student=30,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)
        self.url = reverse(
            "users:admin_permission",
            kwargs={"account_id": self.target_user.id},
        )

    def test_change_role_to_user(self) -> None:
        """USER로 권한 변경"""
        response = self.client.patch(self.url, data={"role": "USER"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.role, "USER")

    def test_change_role_to_admin(self) -> None:
        """ADMIN으로 권한 변경"""
        response = self.client.patch(self.url, data={"role": "ADMIN"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.role, "ADMIN")

    def test_change_role_to_student(self) -> None:
        """STUDENT로 권한 변경 - cohort_id 필요"""
        response = self.client.patch(
            self.url,
            data={"role": "STUDENT", "cohort_id": self.cohort.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.role, "STUDENT")
        self.assertTrue(
            CohortStudents.objects.filter(
                user=self.target_user,
                cohort=self.cohort,
            ).exists()
        )

    def test_change_role_to_ta(self) -> None:
        """TA로 권한 변경 - cohort_id 필요"""
        response = self.client.patch(
            self.url,
            data={"role": "TA", "cohort_id": self.cohort.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.role, "TA")
        self.assertTrue(
            TrainigAssistants.objects.filter(
                user=self.target_user,
                cohort=self.cohort,
            ).exists()
        )

    def test_change_role_to_om(self) -> None:
        """OM으로 권한 변경 - assigned_courses 필요"""
        response = self.client.patch(
            self.url,
            data={"role": "OM", "assigned_courses": [self.course.id]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.role, "OM")
        self.assertTrue(
            OperationManagers.objects.filter(
                user=self.target_user,
                course=self.course,
            ).exists()
        )

    def test_change_role_to_lc(self) -> None:
        """LC로 권한 변경 - assigned_courses 필요"""
        response = self.client.patch(
            self.url,
            data={"role": "LC", "assigned_courses": [self.course.id]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.role, "LC")
        self.assertTrue(
            LearningCoachs.objects.filter(
                user=self.target_user,
                course=self.course,
            ).exists()
        )

    def test_previous_role_data_cleared(self) -> None:
        """역할 변경 시 기존 테이블 데이터 삭제"""
        OperationManagers.objects.create(user=self.target_user, course=self.course)
        self.target_user.role = "OM"
        self.target_user.save()

        response = self.client.patch(self.url, data={"role": "USER"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(OperationManagers.objects.filter(user=self.target_user).exists())

    def test_student_without_cohort_id(self) -> None:
        """STUDENT 권한 변경 시 cohort_id 없으면 400"""
        response = self.client.patch(self.url, data={"role": "STUDENT"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)

    def test_om_without_assigned_courses(self) -> None:
        """OM 권한 변경 시 assigned_courses 없으면 400"""
        response = self.client.patch(self.url, data={"role": "OM"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)

    def test_invalid_role(self) -> None:
        """존재하지 않는 role - 400"""
        response = self.client.patch(self.url, data={"role": "INVALID"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_not_found(self) -> None:
        """존재하지 않는 유저 - 404"""
        url = reverse("users:admin_permission", kwargs={"account_id": 99999})
        response = self.client.patch(url, data={"role": "USER"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["error_detail"],
            "사용자 정보를 찾을 수 없습니다.",
        )

    def test_unauthenticated(self) -> None:
        """비로그인 시 401"""
        self.client.force_authenticate(user=None)
        response = self.client.patch(self.url, data={"role": "USER"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_admin_forbidden(self) -> None:
        """어드민 아닌 유저는 403"""
        non_admin = User.objects.create_user(
            email="user@test.com",
            password="Test1234!",
            name="일반유저",
            nickname="일반닉",
            phone_number="01055556666",
            role=User.Role.USER,
        )
        self.client.force_authenticate(user=non_admin)
        response = self.client.patch(self.url, data={"role": "USER"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

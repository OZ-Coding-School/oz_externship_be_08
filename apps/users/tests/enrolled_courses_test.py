from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.courses.models.cohort import Cohort, StatusChoices
from apps.courses.models.course import Course
from apps.users.models import StudentEnrollmentRequests, User


class MyCoursesViewTest(APITestCase):
    user: User
    other_user: User
    non_student: User
    course: Course
    cohort_preparing: Cohort
    cohort_in_progress: Cohort
    cohort_finished: Cohort
    cohort_pending: Cohort
    cohort_rejected: Cohort
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = reverse("users:enrolled_courses")

        cls.user = User.objects.create_user(
            email="user@test.com",
            password="Test1234!",
            name="테스트",
            nickname="테스트닉",
            phone_number="01011112222",
            role=User.Role.STUDENT,
        )
        cls.other_user = User.objects.create_user(
            email="other@test.com",
            password="Test1234!",
            name="다른유저",
            nickname="다른닉",
            phone_number="01033334444",
            role=User.Role.STUDENT,
        )
        cls.non_student = User.objects.create_user(
            email="nonstudent@test.com",
            password="Test1234!",
            name="일반유저",
            nickname="일반닉2",
            phone_number="01077778888",
            role=User.Role.USER,
        )
        cls.course = Course.objects.create(
            name="백엔드",
            tag="BE",
            thumbnail_img_url="https://example.com/thumb.png",
        )
        cls.cohort_preparing = Cohort.objects.create(
            course=cls.course,
            number=1,
            max_student=30,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 6, 30),
            status=StatusChoices.PREPARING,
        )
        cls.cohort_in_progress = Cohort.objects.create(
            course=cls.course,
            number=2,
            max_student=30,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            status=StatusChoices.IN_PROGRESS,
        )
        cls.cohort_finished = Cohort.objects.create(
            course=cls.course,
            number=3,
            max_student=30,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            status=StatusChoices.FINISHED,
        )
        cls.cohort_pending = Cohort.objects.create(
            course=cls.course,
            number=4,
            max_student=30,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            status=StatusChoices.PREPARING,
        )
        cls.cohort_rejected = Cohort.objects.create(
            course=cls.course,
            number=5,
            max_student=30,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            status=StatusChoices.PREPARING,
        )
        StudentEnrollmentRequests.objects.create(
            user=cls.user,
            cohort=cls.cohort_preparing,
            status=StudentEnrollmentRequests.Status.ACCEPTED,
        )
        StudentEnrollmentRequests.objects.create(
            user=cls.user,
            cohort=cls.cohort_in_progress,
            status=StudentEnrollmentRequests.Status.ACCEPTED,
        )
        StudentEnrollmentRequests.objects.create(
            user=cls.user,
            cohort=cls.cohort_finished,
            status=StudentEnrollmentRequests.Status.ACCEPTED,
        )
        StudentEnrollmentRequests.objects.create(
            user=cls.user,
            cohort=cls.cohort_pending,
            status=StudentEnrollmentRequests.Status.PENDING,
        )
        StudentEnrollmentRequests.objects.create(
            user=cls.user,
            cohort=cls.cohort_rejected,
            status=StudentEnrollmentRequests.Status.REJECTED,
        )

    def setUp(self) -> None:
        self.client = APIClient()

    def test_get_my_courses_success(self) -> None:
        """승인된 기수만 응답에 포함"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        cohort_ids = [item["cohort"]["id"] for item in response.data]
        self.assertIn(self.cohort_preparing.id, cohort_ids)
        self.assertIn(self.cohort_in_progress.id, cohort_ids)
        self.assertIn(self.cohort_finished.id, cohort_ids)

    def test_pending_and_rejected_excluded(self) -> None:
        """PENDING, REJECTED 상태는 응답에서 제외"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        cohort_ids = [item["cohort"]["id"] for item in response.data]
        self.assertNotIn(self.cohort_pending.id, cohort_ids)
        self.assertNotIn(self.cohort_rejected.id, cohort_ids)

    def test_response_structure(self) -> None:
        """응답 구조 검증"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        item = next(i for i in response.data if i["cohort"]["id"] == self.cohort_preparing.id)

        cohort_data = item["cohort"]
        self.assertEqual(cohort_data["id"], self.cohort_preparing.id)
        self.assertEqual(cohort_data["number"], 1)
        self.assertIn("start_date", cohort_data)
        self.assertIn("end_date", cohort_data)
        self.assertEqual(cohort_data["status"], StatusChoices.PREPARING)

        course_data = item["course"]
        self.assertEqual(course_data["id"], self.course.id)
        self.assertEqual(course_data["name"], "백엔드")
        self.assertEqual(course_data["tag"], "BE")
        self.assertEqual(course_data["thumbnail_img_url"], "https://example.com/thumb.png")

    def test_includes_all_cohort_statuses(self) -> None:
        """수강 예정/진행 중/완료 모든 status 포함"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        cohort_statuses = [item["cohort"]["status"] for item in response.data]
        self.assertIn(StatusChoices.PREPARING, cohort_statuses)
        self.assertIn(StatusChoices.IN_PROGRESS, cohort_statuses)
        self.assertIn(StatusChoices.FINISHED, cohort_statuses)

    def test_other_user_sees_only_own_courses(self) -> None:
        """다른 유저는 본인 수강 목록만 보임"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_non_student_forbidden(self) -> None:
        """수강생 아닌 유저는 403"""
        self.client.force_authenticate(user=self.non_student)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error_detail", response.data)

    def test_unauthenticated(self) -> None:
        """비로그인 시 401"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error_detail", response.data)
        self.assertEqual(
            response.data["error_detail"],
            "자격 인증 데이터가 제공되지 않았습니다.",
        )

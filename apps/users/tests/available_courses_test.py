from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.courses.models.cohort import Cohort, StatusChoices
from apps.courses.models.course import Course
from apps.users.models import StudentEnrollmentRequests, User


class AvailableCoursesViewTest(APITestCase):
    user: User
    other_user: User
    course: Course
    cohort_in_progress: Cohort
    cohort_preparing: Cohort
    cohort_finished: Cohort
    cohort_already_applied: Cohort
    cohort_already_accepted: Cohort
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = reverse("users:available-courses")

        cls.user = User.objects.create_user(
            email="user@test.com",
            password="Test1234!",
            name="테스트",
            nickname="테스트닉",
            phone_number="01011112222",
        )

        cls.other_user = User.objects.create_user(
            email="other@test.com",
            password="Test1234!",
            name="다른유저",
            nickname="다른닉",
            phone_number="01033334444",
        )

        cls.course = Course.objects.create(name="백엔드", tag="BE")

        # 모집 중 (IN_PROGRESS) - 정상 노출되어야 함
        cls.cohort_in_progress = Cohort.objects.create(
            course=cls.course,
            number=1,
            max_student=30,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            status=StatusChoices.IN_PROGRESS,
        )

        # 준비중 - 노출 안 됨
        cls.cohort_preparing = Cohort.objects.create(
            course=cls.course,
            number=2,
            max_student=30,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            status=StatusChoices.PREPARING,
        )

        # 종료 - 노출 안 됨
        cls.cohort_finished = Cohort.objects.create(
            course=cls.course,
            number=3,
            max_student=30,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            status=StatusChoices.FINISHED,
        )

        # 모집 중인데 이미 신청 중 - 노출 안 됨
        cls.cohort_already_applied = Cohort.objects.create(
            course=cls.course,
            number=4,
            max_student=30,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            status=StatusChoices.IN_PROGRESS,
        )
        StudentEnrollmentRequests.objects.create(
            user=cls.user,
            cohort=cls.cohort_already_applied,
            status=StudentEnrollmentRequests.Status.PENDING,
        )

        # 모집 중인데 이미 승인됨 - 노출 안 됨
        cls.cohort_already_accepted = Cohort.objects.create(
            course=cls.course,
            number=5,
            max_student=30,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            status=StatusChoices.IN_PROGRESS,
        )
        StudentEnrollmentRequests.objects.create(
            user=cls.user,
            cohort=cls.cohort_already_accepted,
            status=StudentEnrollmentRequests.Status.ACCEPTED,
        )

    def setUp(self) -> None:
        self.client = APIClient()

    def test_get_available_cohorts_success(self) -> None:
        """모집 중 + 본인 미신청인 기수만 반환"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # cohort_in_progress 1개만 나와야 함
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["cohort"]["id"], self.cohort_in_progress.id)

    def test_response_structure(self) -> None:
        """응답 구조 확인 - cohort, course 중첩"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        item = response.data[0]
        self.assertIn("cohort", item)
        self.assertIn("course", item)

        # cohort 필드 검증
        cohort_data = item["cohort"]
        self.assertEqual(cohort_data["id"], self.cohort_in_progress.id)
        self.assertEqual(cohort_data["number"], 1)
        self.assertIn("start_date", cohort_data)
        self.assertIn("end_date", cohort_data)
        self.assertEqual(cohort_data["status"], StatusChoices.IN_PROGRESS)

        # course 필드 검증
        course_data = item["course"]
        self.assertEqual(course_data["id"], self.course.id)
        self.assertEqual(course_data["name"], "백엔드")

    def test_other_user_sees_all_in_progress_cohorts(self) -> None:
        """다른 유저는 신청 안 했으니 모집 중 기수 다 보임"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # IN_PROGRESS 기수 3개 (in_progress, already_applied, already_accepted)
        # other_user는 신청 안 했으니 다 나옴
        self.assertEqual(len(response.data), 3)

    def test_no_available_cohorts_returns_empty(self) -> None:
        """수강 가능한 기수 없으면 빈 배열"""
        # 모든 IN_PROGRESS 기수에 신청
        StudentEnrollmentRequests.objects.create(
            user=self.user,
            cohort=self.cohort_in_progress,
            status=StudentEnrollmentRequests.Status.PENDING,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_rejected_or_canceled_does_not_exclude(self) -> None:
        """거절/취소된 신청은 다시 신청 가능"""
        # cohort_in_progress에 거절된 기록 추가
        StudentEnrollmentRequests.objects.create(
            user=self.user,
            cohort=self.cohort_in_progress,
            status=StudentEnrollmentRequests.Status.REJECTED,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 거절돼도 다시 보여야 함
        cohort_ids = [item["cohort"]["id"] for item in response.data]
        self.assertIn(self.cohort_in_progress.id, cohort_ids)

    def test_unauthenticated(self) -> None:
        """비로그인 시 401"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error_detail", response.data)
        self.assertEqual(
            response.data["error_detail"],
            "자격 인증 데이터가 제공되지 않았습니다.",
        )

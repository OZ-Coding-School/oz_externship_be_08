from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.courses.models.cohort import Cohort
from apps.courses.models.course import Course
from apps.users.models import StudentEnrollmentRequests, User


class EnrollmentTest(APITestCase):
    user: User
    url: str
    cohort: Cohort
    course: Course

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = reverse("users:enroll-student")
        cls.user = User.objects.create_user(
            email="test@test.com",
            password="Test1234!",
            name="테스트",
            nickname="테스트닉",
            phone_number="01012345678",
        )
        cls.course = Course.objects.create(
            name="백엔드 부트캠프",
            tag="BE",
        )
        cls.cohort = Cohort.objects.create(
            course=cls.course,
            number=1,
            max_student=30,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_enrollment_success(self) -> None:
        response = self.client.post(self.url, data={"cohort_id": self.cohort.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            StudentEnrollmentRequests.objects.filter(
                user=self.user, cohort_id=self.cohort.id, status="pending"
            ).exists()
        )

    def test_enrollment_duplicate(self) -> None:
        # 첫 번째 신청
        self.client.post(self.url, data={"cohort_id": self.cohort.id})
        # 두 번째 중복 신청
        response = self.client.post(self.url, data={"cohort_id": self.cohort.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_enrollment_unauthenticated(self) -> None:
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, data={"cohort_id": self.cohort.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_enrollment_invalid_cohort(self) -> None:
        response = self.client.post(self.url, data={"cohort_id": 99999})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

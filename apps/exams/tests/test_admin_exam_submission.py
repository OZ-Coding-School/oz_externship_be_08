from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.courses.models import Cohort
from apps.exams.models import Exam, ExamDeployment, ExamSubmission
from apps.posts.models import Subject
from apps.posts.models.course import Course
from apps.users.models import User


class TestAdminExamSubmissionListAPI(APITestCase):
    user: User
    admin: User
    course: Course
    subject: Subject
    cohort: Cohort
    exam1: Exam
    exam2: Exam
    deployment1: ExamDeployment
    deployment2: ExamDeployment
    submission1: ExamSubmission
    submission2: ExamSubmission
    url: str
    error_401: str
    error_403: str
    error_400: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="test@test.com",
            password="test1234!",
            name="테스터",
            nickname="tester",
            phone_number="010-1234-5678",
            is_active=True,
            role="STUDENT",
        )
        cls.admin = User.objects.create_superuser(
            email="admin@test.com",
            password="test1234!",
            name="관리자",
            nickname="admin",
            phone_number="010-2222-5678",
            is_active=True,
            role="ADMIN",
        )

        cls.course = Course.objects.create(name="웹 개발", tag="WEB")
        cls.subject = Subject.objects.create(
            course=cls.course,
            title="Python",
            number_of_days=30,
            number_of_hours=60,
        )
        cls.cohort = Cohort.objects.create(
            course=cls.course,
            number=1,
            max_student=30,
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        cls.exam1 = Exam.objects.create(subject=cls.subject, title="시험1")
        cls.exam2 = Exam.objects.create(subject=cls.subject, title="시험2")

        cls.deployment1 = ExamDeployment.objects.create(
            exam=cls.exam1,
            cohort=cls.cohort,
            access_code="access-code-1",
            open_at="2024-01-01T00:00:00Z",
            close_at="2024-12-31T23:59:59Z",
        )
        cls.deployment2 = ExamDeployment.objects.create(
            exam=cls.exam2,
            cohort=cls.cohort,
            access_code="access-code-2",
            open_at="2024-01-01T00:00:00Z",
            close_at="2024-12-31T23:59:59Z",
        )

        cls.submission1 = ExamSubmission.objects.create(
            submitter=cls.user,
            deployment=cls.deployment1,
            started_at=timezone.now(),
            score=80,
            correct_answer_count=8,
        )
        cls.submission2 = ExamSubmission.objects.create(
            submitter=cls.admin,
            deployment=cls.deployment2,
            started_at=timezone.now(),
            score=90,
            correct_answer_count=9,
        )

        cls.url = reverse("exam-submission-list")
        cls.error_401 = "자격 인증 데이터가 제공되지 않았습니다."
        cls.error_403 = "쪽지시험 응시 내역 조회 권한이 없습니다."
        cls.error_400 = "유효하지 않은 조회 요청입니다."

    def setUp(self) -> None:
        self.client = APIClient()

    # 권한
    def test_submission_list_as_admin(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_submission_list_as_user(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error_detail"), self.error_403)

    def test_submission_list_as_anonymous(self) -> None:
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get("error_detail"), self.error_401)

    # 조회 결과 없음
    def test_submission_list_not_found(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {"search_keyword": "존재하지않는이름"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    # 필터링
    def test_submission_list_filter_by_cohort_id(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {"cohort_id": self.cohort.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_submission_list_filter_by_exam_id(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {"exam_id": self.exam1.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["exam_title"], "시험1")

    # 검색
    def test_submission_list_search_by_nickname(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {"search_keyword": "tester"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["nickname"], "tester")

    def test_submission_list_search_by_name(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {"search_keyword": "테스터"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "테스터")

    # 정렬
    def test_submission_list_sort_by_score_desc(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {"sort": "score", "order": "desc"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["score"], 90)

    def test_submission_list_sort_by_score_asc(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {"sort": "score", "order": "asc"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["score"], 80)

    # 유효하지 않은 파라미터
    def test_submission_list_invalid_sort(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {"sort": "잘못된값"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error_detail"), self.error_400)

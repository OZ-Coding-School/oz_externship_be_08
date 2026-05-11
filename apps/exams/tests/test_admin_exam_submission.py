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


class TestAdminExamSubmissionDetailAPI(APITestCase):
    user: User
    admin: User
    course: Course
    subject: Subject
    cohort: Cohort
    exam: Exam
    deployment: ExamDeployment
    submission: ExamSubmission
    url: str
    error_401: str
    error_403: str
    error_404: str
    error_400: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="detail_test@test.com",
            password="test1234!",
            name="테스터",
            nickname="tester2",
            phone_number="010-3333-5678",
            is_active=True,
            role="STUDENT",
        )
        cls.admin = User.objects.create_superuser(
            email="detail_admin@test.com",
            password="test1234!",
            name="관리자",
            nickname="admin2",
            phone_number="010-4444-5678",
            is_active=True,
            role="ADMIN",
        )

        cls.course = Course.objects.create(name="백엔드 개발", tag="WEB")
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

        cls.exam = Exam.objects.create(subject=cls.subject, title="Python 기본 문법 테스트")

        cls.deployment = ExamDeployment.objects.create(
            exam=cls.exam,
            cohort=cls.cohort,
            access_code="access-code-detail",
            open_at="2024-01-01T00:00:00Z",
            close_at="2024-12-31T23:59:59Z",
            questions_snapshot_json=[
                {
                    "id": 1,
                    "type": "multiple_choice",
                    "question": "Python의 특징은?",
                    "prompt": None,
                    "options": ["인터프리터 언어", "정적 타입", "메모리 수동 관리"],
                    "point": 10,
                    "answer": "인터프리터 언어",
                    "explanation": "Python은 인터프리터 언어입니다.",
                }
            ],
        )

        cls.submission = ExamSubmission.objects.create(
            submitter=cls.user,
            deployment=cls.deployment,
            started_at=timezone.now(),
            score=80,
            correct_answer_count=1,
            cheating_count=0,
            answer_json={
                "1": ["인터프리터 언어"],
            },
        )

        cls.url = reverse("exam-submission-detail", kwargs={"submission_id": cls.submission.id})
        cls.error_401 = "자격 인증 데이터가 제공되지 않았습니다."
        cls.error_403 = "쪽지시험 응시 상세 조회 권한이 없습니다."
        cls.error_404 = "해당 응시 내역을 찾을 수 없습니다."
        cls.error_400 = "유효하지 않은 상세 조회 요청입니다."

    def setUp(self) -> None:
        self.client = APIClient()

    # 권한
    def test_submission_detail_as_admin(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_submission_detail_as_user(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error_detail"), self.error_403)

    def test_submission_detail_as_anonymous(self) -> None:
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get("error_detail"), self.error_401)

    # 조회 성공
    def test_submission_detail_success(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["exam"]["exam_title"], "Python 기본 문법 테스트")
        self.assertEqual(response.data["student"]["nickname"], "tester2")
        self.assertEqual(response.data["result"]["score"], 80)
        self.assertEqual(len(response.data["questions"]), 1)

    # 404
    def test_submission_detail_not_found(self) -> None:
        self.client.force_authenticate(user=self.admin)
        url = reverse("exam-submission-detail", kwargs={"submission_id": 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error_detail"), self.error_404)

    # 유효하지 않은 파라미터
    def test_submission_detail_invalid_id(self) -> None:
        self.client.force_authenticate(user=self.admin)
        url = reverse("exam-submission-detail", kwargs={"submission_id": 0})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error_detail"), self.error_400)


class TestAdminExamSubmissionDeleteAPI(APITestCase):
    user: User
    admin: User
    course: Course
    subject: Subject
    cohort: Cohort
    exam: Exam
    deployment: ExamDeployment
    submission: ExamSubmission
    url: str
    error_401: str
    error_403: str
    error_404: str
    error_400: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="delete_test@test.com",
            password="test1234!",
            name="테스터",
            nickname="tester3",
            phone_number="010-5555-5678",
            is_active=True,
            role="STUDENT",
        )
        cls.admin = User.objects.create_superuser(
            email="delete_admin@test.com",
            password="test1234!",
            name="관리자",
            nickname="admin3",
            phone_number="010-6666-5678",
            is_active=True,
            role="ADMIN",
        )

        cls.course = Course.objects.create(name="풀스택 개발", tag="WEB")
        cls.subject = Subject.objects.create(
            course=cls.course,
            title="Django",
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

        cls.exam = Exam.objects.create(subject=cls.subject, title="Django 테스트")

        cls.deployment = ExamDeployment.objects.create(
            exam=cls.exam,
            cohort=cls.cohort,
            access_code="access-code-delete",
            open_at="2024-01-01T00:00:00Z",
            close_at="2024-12-31T23:59:59Z",
        )

        cls.error_401 = "자격 인증 데이터가 제공되지 않았습니다."
        cls.error_403 = "쪽지시험 응시 내역 삭제 권한이 없습니다."
        cls.error_404 = "삭제할 응시 내역을 찾을 수 없습니다."
        cls.error_400 = "유효하지 않은 응시 내역 삭제 요청입니다."

    def setUp(self) -> None:
        self.client = APIClient()
        self.submission = ExamSubmission.objects.create(
            submitter=self.user,
            deployment=self.deployment,
            started_at=timezone.now(),
            score=70,
            correct_answer_count=7,
        )
        self.url = reverse("exam-submission-detail", kwargs={"submission_id": self.submission.id})

    # 권한
    def test_submission_delete_as_admin(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("submission_id"), self.submission.id)

    def test_submission_delete_as_user(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error_detail"), self.error_403)

    def test_submission_delete_as_anonymous(self) -> None:
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get("error_detail"), self.error_401)

    # 삭제 성공
    def test_submission_delete_success(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(ExamSubmission.objects.filter(id=self.submission.id).exists())

    # 404
    def test_submission_delete_not_found(self) -> None:
        self.client.force_authenticate(user=self.admin)
        url = reverse("exam-submission-detail", kwargs={"submission_id": 99999})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error_detail"), self.error_404)

    # 유효하지 않은 파라미터
    def test_submission_delete_invalid_id(self) -> None:
        self.client.force_authenticate(user=self.admin)
        url = reverse("exam-submission-detail", kwargs={"submission_id": 0})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error_detail"), self.error_400)

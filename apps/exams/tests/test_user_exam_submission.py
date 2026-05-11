from typing import Any

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.exams.models import Exam, ExamDeployment, ExamQuestion, ExamSubmission
from apps.posts.models import Cohort, Course, Subject
from apps.users.models import User


class BaseTestCase(APITestCase):
    student1: User
    student2: User
    admin: User
    normal_user: User
    course1: Course
    course2: Course
    subject1: Subject
    subject2: Subject
    cohort1: Cohort
    cohort2: Cohort
    exam1: Exam
    exam2: Exam
    question1: ExamQuestion
    question2: ExamQuestion
    question3: ExamQuestion
    question4: ExamQuestion
    deployment1: ExamDeployment
    deployment2: ExamDeployment
    submission1: ExamSubmission
    submission2: ExamSubmission

    @classmethod
    def setUpTestData(cls) -> None:
        cls.student1 = User.objects.create_user(
            email="student1@test.com",
            password="test1234!",
            name="수강생1",
            nickname="student1",
            phone_number="010-1111-1111",
            is_active=True,
            role="STUDENT",
        )
        cls.student2 = User.objects.create_user(
            email="student2@test.com",
            password="test1234!",
            name="수강생2",
            nickname="student2",
            phone_number="010-2222-2222",
            is_active=True,
            role="STUDENT",
        )
        cls.admin = User.objects.create_superuser(
            email="admin@test.com",
            password="test1234!",
            name="관리자",
            nickname="admin",
            phone_number="010-3333-3333",
            is_active=True,
            role="ADMIN",
        )
        cls.normal_user = User.objects.create_user(
            email="user@test.com",
            password="test1234!",
            name="일반유저",
            nickname="normaluser",
            phone_number="010-4444-4444",
            is_active=True,
            role="USER",
        )

        cls.course1 = Course.objects.create(name="웹 개발", tag="WEB")
        cls.course2 = Course.objects.create(name="데이터 분석", tag="DAT")

        cls.subject1 = Subject.objects.create(
            course=cls.course1,
            title="html",
            number_of_days=30,
            number_of_hours=60,
        )
        cls.subject2 = Subject.objects.create(
            course=cls.course2,
            title="python",
            number_of_days=40,
            number_of_hours=80,
        )

        cls.cohort1 = Cohort.objects.create(
            course=cls.course1,
            number=1,
            max_student=30,
            start_date="2024-01-01",
            end_date="2024-12-31",
        )
        cls.cohort2 = Cohort.objects.create(
            course=cls.course2,
            number=1,
            max_student=25,
            start_date="2024-03-01",
            end_date="2025-02-28",
        )

        cls.exam1 = Exam.objects.create(subject=cls.subject1, title="HTML 중간고사")
        cls.exam2 = Exam.objects.create(subject=cls.subject2, title="Python 기말고사")

        cls.question1 = ExamQuestion.objects.create(
            exam=cls.exam1,
            question="HTML의 약자는?",
            type="single_choice",
            options_json='["HyperText Markup Language", "High Tech ML", "Hyper Transfer ML"]',
            answer=["HyperText Markup Language"],
            point=5,
            explanation="HTML은 HyperText Markup Language의 약자입니다.",
        )
        cls.question2 = ExamQuestion.objects.create(
            exam=cls.exam1,
            question="div 태그의 용도는?",
            type="short_answer",
            answer=["영역 나누기"],
            point=5,
            explanation="div는 블록 레벨 컨테이너입니다.",
        )
        cls.question3 = ExamQuestion.objects.create(
            exam=cls.exam2,
            question="파이썬의 자료형을 모두 고르시오",
            type="multiple_choice",
            options_json='["int", "str", "html", "list"]',
            answer=["int", "str", "list"],
            point=4,
            explanation="html은 파이썬 자료형이 아닙니다.",
        )
        cls.question4 = ExamQuestion.objects.create(
            exam=cls.exam2,
            question="___는 파이썬의 패키지 관리자이다",
            type="fill_blank",
            prompt="___는 파이썬의 패키지 관리자이다",
            blank_count=1,
            answer=["pip"],
            point=6,
            explanation="pip는 파이썬의 기본 패키지 관리자입니다.",
        )

        cls.deployment1 = ExamDeployment.objects.create(
            exam=cls.exam1,
            cohort=cls.cohort1,
            access_code="access-code-1",
            open_at="2024-01-01T00:00:00Z",
            close_at="2024-12-31T23:59:59Z",
            questions_snapshot_json=[
                {"id": cls.question1.id, "question": "HTML의 약자는?", "point": 5},
                {"id": cls.question2.id, "question": "div 태그의 용도는?", "point": 5},
            ],
        )
        cls.deployment2 = ExamDeployment.objects.create(
            exam=cls.exam2,
            cohort=cls.cohort2,
            access_code="access-code-2",
            open_at="2024-03-01T00:00:00Z",
            close_at="2025-02-28T23:59:59Z",
            questions_snapshot_json=[
                {"id": cls.question3.id, "question": "파이썬의 자료형을 모두 고르시오", "point": 4},
                {"id": cls.question4.id, "question": "___는 파이썬의 패키지 관리자이다", "point": 6},
            ],
        )

        cls.submission1 = ExamSubmission.objects.create(
            submitter=cls.student1,
            deployment=cls.deployment1,
            started_at=timezone.now(),
            cheating_count=0,
            answer_json={
                str(cls.question1.id): ["HyperText Markup Language"],
                str(cls.question2.id): ["영역 나누기"],
            },
            score=10,
            correct_answer_count=2,
        )
        cls.submission2 = ExamSubmission.objects.create(
            submitter=cls.student2,
            deployment=cls.deployment2,
            started_at=timezone.now(),
            cheating_count=1,
            answer_json={
                str(cls.question3.id): ["int", "str"],
                str(cls.question4.id): ["pip"],
            },
            score=6,
            correct_answer_count=1,
        )


class TestUserExamSubmissionGet(BaseTestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    # 권한
    def test_get_submission_as_correct_user(self) -> None:
        self.client.force_authenticate(user=self.student1)

        response = self.client.get(reverse("user-exam-submission-get", kwargs={"submission_id": self.submission1.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.submission1.id)
        self.assertEqual(response.data["submitter_id"], self.student1.id)
        self.assertEqual(response.data["deployment_id"], self.deployment1.id)
        self.assertEqual(response.data["exam"]["id"], self.exam1.id)
        self.assertEqual(response.data["questions"][0]["question"], "HTML의 약자는?")
        self.assertEqual(response.data["total_score"], 10)
        self.assertEqual(response.data["score"], 10)
        self.assertEqual(response.data["correct_answer_count"], 2)

    def test_get_submission_as_ather_student(self) -> None:
        self.client.force_authenticate(user=self.student2)

        response = self.client.get(reverse("user-exam-submission-get", kwargs={"submission_id": self.submission1.id}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "해당 시험 정보를 찾을 수 없습니다.")

    def test_get_submission_as_normal_user(self) -> None:
        self.client.force_authenticate(user=self.normal_user)

        response = self.client.get(reverse("user-exam-submission-get", kwargs={"submission_id": self.submission1.id}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "권한이 없습니다.")

    def test_get_submission_as_unauthenticated_user(self) -> None:

        response = self.client.get(reverse("user-exam-submission-get", kwargs={"submission_id": self.submission1.id}))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")


class TestUserExamSubmissionCreate(APITestCase):
    student: User
    normal_user: User
    course: Course
    subject: Subject
    cohort: Cohort
    exam: Exam
    question: ExamQuestion
    deployment: ExamDeployment
    url: str
    error_401: str
    error_403: str
    error_400: str
    error_404: str
    error_409: str

    @classmethod
    def setUpTestData(cls) -> None:
        cls.student = User.objects.create_user(
            email="create_student@test.com",
            password="test1234!",
            name="제출학생",
            nickname="c_student",
            phone_number="010-5555-5555",
            is_active=True,
            role="STUDENT",
        )
        cls.normal_user = User.objects.create_user(
            email="create_normal@test.com",
            password="test1234!",
            name="일반유저",
            nickname="c_normal",
            phone_number="010-6666-6666",
            is_active=True,
            role="USER",
        )

        cls.course = Course.objects.create(name="백엔드", tag="WEB")
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
        cls.question = ExamQuestion.objects.create(
            exam=cls.exam,
            question="Django는 Python 웹 프레임워크이다",
            type="ox",
            answer=["O"],
            point=10,
            explanation="맞습니다.",
        )
        cls.deployment = ExamDeployment.objects.create(
            exam=cls.exam,
            cohort=cls.cohort,
            access_code="create-access-code",
            open_at="2024-01-01T00:00:00Z",
            close_at="2024-12-31T23:59:59Z",
            questions_snapshot_json=[
                {
                    "id": cls.question.id,
                    "type": "ox",
                    "question": "Django는 Python 웹 프레임워크이다",
                    "answer": ["O"],
                    "point": 10,
                    "explanation": "맞습니다.",
                }
            ],
        )

        cls.url = reverse("user-exam-submission-create")
        cls.error_401 = "자격 인증 데이터가 제공되지 않았습니다."
        cls.error_403 = "권한이 없습니다."
        cls.error_400 = "유효하지 않은 시험 응시 세션입니다."
        cls.error_404 = "해당 시험 정보를 찾을 수 없습니다."
        cls.error_409 = "이미 제출된 시험입니다."

    def setUp(self) -> None:
        self.client = APIClient()

    def get_valid_data(self) -> dict[str, Any]:
        return {
            "deployment_id": self.deployment.id,
            "started_at": "2024-01-01T10:00:00Z",
            "cheating_count": 0,
            "answers": [
                {
                    "question_id": self.question.id,
                    "type": "ox",
                    "submitted_answer": "O",
                }
            ],
        }

    # 권한
    def test_create_submission_as_student(self) -> None:
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.url, self.get_valid_data(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_submission_as_anonymous(self) -> None:
        response = self.client.post(self.url, self.get_valid_data(), format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get("error_detail"), self.error_401)

    def test_create_submission_as_normal_user(self) -> None:
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(self.url, self.get_valid_data(), format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error_detail"), self.error_403)

    # 제출 성공
    def test_create_submission_success(self) -> None:
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.url, self.get_valid_data(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("submission_id", response.data)
        self.assertEqual(response.data["score"], 10)
        self.assertEqual(response.data["correct_answer_count"], 1)
        self.assertEqual(response.data["redirect_url"], f"/exam/result/{response.data['submission_id']}")

    # 400
    def test_create_submission_invalid_data(self) -> None:
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error_detail"), self.error_400)

    # 404
    def test_create_submission_deployment_not_found(self) -> None:
        self.client.force_authenticate(user=self.student)
        data = self.get_valid_data()
        data["deployment_id"] = 99999
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error_detail"), self.error_404)

    # 409
    def test_create_submission_already_exists(self) -> None:
        ExamSubmission.objects.create(
            submitter=self.student,
            deployment=self.deployment,
            started_at=timezone.now(),
            score=10,
            correct_answer_count=1,
        )
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.url, self.get_valid_data(), format="json")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data.get("error_detail"), self.error_409)

from datetime import timedelta
from typing import Any
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.courses.models.cohort import Cohort
from apps.courses.models.course import Course
from apps.courses.models.subject import Subject
from apps.exams.models.exam_deployment_model import ExamDeployment
from apps.exams.models.exam_model import Exam
from apps.exams.models.exam_question_model import ExamQuestion
from apps.users.models import User


class DeploymentBaseTestCase(APITestCase):
    admin_user: User
    user: User
    student: User
    course: Course
    subject: Subject
    exam: Exam
    exam_no_questions: Exam
    cohort: Cohort
    cohort2: Cohort
    cohort3: Cohort
    deployment: ExamDeployment
    deployment2: ExamDeployment
    list_url: str
    detail_url: str
    detail2_url: str
    invalid_url: str
    not_found_url: str
    status_url: str
    status_invalid_url: str
    status_not_found_url: str
    create_data: dict[str, Any]
    update_data: dict[str, Any]

    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin_user = User.objects.create_superuser(
            email="admin@test.com",
            name="admin",
            nickname="admin",
            phone_number="01011111111",
            is_active=True,
            role=User.Role.ADMIN,
            password="test_password",
        )
        cls.user = User.objects.create_user(
            email="user@test.com",
            name="user",
            nickname="user",
            phone_number="01022222222",
            is_active=True,
            role=User.Role.USER,
            password="test_password",
        )
        cls.student = User.objects.create_user(
            email="student@test.com",
            name="student",
            nickname="student",
            phone_number="01033333333",
            is_active=True,
            role=User.Role.STUDENT,
            password="test_password",
        )

        cls.course = Course.objects.create(name="테스트과정", tag="TST")
        cls.subject = Subject.objects.create(
            course=cls.course,
            title="테스트과목",
            number_of_days=1,
            number_of_hours=1,
        )
        cls.exam = Exam.objects.create(title="테스트시험", subject=cls.subject)
        cls.exam_no_questions = Exam.objects.create(title="문제없는시험", subject=cls.subject)
        ExamQuestion.objects.create(
            exam=cls.exam,
            question="테스트문제",
            answer={"answer": 1},
            type=ExamQuestion.QuestionType.SHORT_ANSWER,
            point=10,
        )

        cls.cohort = Cohort.objects.create(
            course=cls.course, number=1, max_student=30, start_date="2026-01-01", end_date="2026-06-30"
        )
        cls.cohort2 = Cohort.objects.create(
            course=cls.course, number=2, max_student=30, start_date="2026-01-01", end_date="2026-06-30"
        )
        cls.cohort3 = Cohort.objects.create(
            course=cls.course, number=3, max_student=30, start_date="2026-01-01", end_date="2026-06-30"
        )

        now = timezone.now()
        cls.deployment = ExamDeployment.objects.create(
            exam=cls.exam,
            cohort=cls.cohort,
            duration_time=60,
            open_at=now + timedelta(days=1),
            close_at=now + timedelta(days=2),
            access_code="testcode1",
            questions_snapshot_json=[{"question": "test"}],
        )
        cls.deployment2 = ExamDeployment.objects.create(
            exam=cls.exam,
            cohort=cls.cohort2,
            duration_time=60,
            open_at=now + timedelta(days=1),
            close_at=now + timedelta(days=2),
            access_code="testcode2",
            questions_snapshot_json=[{"question": "test"}],
        )

        cls.list_url = reverse("exam-deployment")
        cls.detail_url = reverse("exam-deployment-detail", kwargs={"deployment_id": str(cls.deployment.id)})
        cls.detail2_url = reverse("exam-deployment-detail", kwargs={"deployment_id": str(cls.deployment2.id)})
        cls.invalid_url = reverse("exam-deployment-detail", kwargs={"deployment_id": "abc"})
        cls.not_found_url = reverse("exam-deployment-detail", kwargs={"deployment_id": "99999"})
        cls.status_url = reverse("exam-deployment-status", kwargs={"deployment_id": str(cls.deployment.id)})
        cls.status_invalid_url = reverse("exam-deployment-status", kwargs={"deployment_id": "abc"})
        cls.status_not_found_url = reverse("exam-deployment-status", kwargs={"deployment_id": "99999"})

        cls.create_data = {
            "exam_id": cls.exam.id,
            "cohort_id": cls.cohort3.id,
            "duration_time": 60,
            "open_at": (now + timedelta(days=1)).isoformat(),
            "close_at": (now + timedelta(days=2)).isoformat(),
        }
        cls.update_data = {
            "open_at": (now + timedelta(days=3)).isoformat(),
            "close_at": (now + timedelta(days=4)).isoformat(),
            "duration_time": 30,
        }

    def setUp(self) -> None:
        self.client = APIClient()


class TestDeploymentCreate(DeploymentBaseTestCase):
    """배포 생성 테스트"""

    # 권한 테스트
    def test_admin_create_success(self) -> None:
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.list_url, self.create_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("pk", response.data)

    def test_user_create_forbidden(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, self.create_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error_detail"), "쪽지시험 배포 생성 권한이 없습니다.")

    def test_student_create_forbidden(self) -> None:
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.list_url, self.create_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error_detail"), "쪽지시험 배포 생성 권한이 없습니다.")

    def test_unauth_create_unauthorized(self) -> None:
        response = self.client.post(self.list_url, self.create_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get("error_detail"), "자격 인증 데이터가 제공되지 않았습니다.")

    # 기능 실패 테스트
    def test_create_invalid_open_at_past(self) -> None:
        """open_at이 과거인 경우 400"""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()
        data = {**self.create_data, "open_at": (now - timedelta(days=1)).isoformat()}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_close_at_past(self) -> None:
        """close_at이 과거인 경우 400"""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()
        data = {**self.create_data, "close_at": (now - timedelta(days=1)).isoformat()}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_close_before_open(self) -> None:
        """close_at이 open_at보다 이른 경우 400"""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()
        data = {
            **self.create_data,
            "open_at": (now + timedelta(days=2)).isoformat(),
            "close_at": (now + timedelta(days=1)).isoformat(),
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_exam_not_found(self) -> None:
        """존재하지 않는 시험 ID → 404"""
        self.client.force_authenticate(user=self.admin_user)
        data = {**self.create_data, "exam_id": 99999}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error_detail"), "배포 대상 과정-기수 또는 시험 정보를 찾을 수 없습니다.")

    def test_create_cohort_not_found(self) -> None:
        """존재하지 않는 기수 ID → 404"""
        self.client.force_authenticate(user=self.admin_user)
        data = {**self.create_data, "cohort_id": 99999}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error_detail"), "배포 대상 과정-기수 또는 시험 정보를 찾을 수 없습니다.")

    def test_create_conflict(self) -> None:
        """동일 시험+기수 배포 중복 → 409"""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()
        data = {
            "exam_id": self.exam.id,
            "cohort_id": self.cohort.id,
            "duration_time": 60,
            "open_at": (now + timedelta(days=1)).isoformat(),
            "close_at": (now + timedelta(days=2)).isoformat(),
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data.get("error_detail"), "동일한 조건의 배포가 이미 존재합니다.")

    def test_create_no_questions(self) -> None:
        """문제가 없는 시험 배포 시 400"""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()
        data = {
            "exam_id": self.exam_no_questions.id,
            "cohort_id": self.cohort3.id,
            "duration_time": 60,
            "open_at": (now + timedelta(days=1)).isoformat(),
            "close_at": (now + timedelta(days=2)).isoformat(),
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error_detail"), "유효하지 않은 배포 생성 요청입니다.")

    # 참가코드 테스트
    def test_create_access_code_generated(self) -> None:
        """배포 생성 시 참가코드 자동 생성 확인"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.list_url, self.create_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        deployment = ExamDeployment.objects.get(id=response.data["pk"])
        self.assertIsNotNone(deployment.access_code)
        self.assertNotEqual(deployment.access_code, "")

    def test_create_access_code_unique(self) -> None:
        """서로 다른 배포의 참가코드는 달라야 함"""
        self.assertNotEqual(self.deployment.access_code, self.deployment2.access_code)


class TestDeploymentList(DeploymentBaseTestCase):
    """배포 목록 조회 테스트"""

    # 권한 테스트
    def test_admin_list_success(self) -> None:
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_user_list_forbidden(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error_detail"), "쪽지시험 배포 목록 조회 권한이 없습니다.")

    def test_student_list_forbidden(self) -> None:
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error_detail"), "쪽지시험 배포 목록 조회 권한이 없습니다.")

    def test_unauth_list_unauthorized(self) -> None:
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get("error_detail"), "자격 인증 데이터가 제공되지 않았습니다.")

    # 기능 테스트
    def test_list_filter_by_subject(self) -> None:
        """과목 필터링 - 해당 과목 배포만 조회"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url, {"subject_id": self.subject.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_list_filter_by_cohort(self) -> None:
        """기수 필터링 - 해당 기수 배포만 조회"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url, {"cohort_id": self.cohort.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_list_filter_by_subject_no_result(self) -> None:
        """존재하지 않는 과목 필터링 - 빈 결과"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url, {"subject_id": 99999})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_list_search_keyword(self) -> None:
        """키워드 검색 - 시험 이름 검색"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url, {"search_keyword": "테스트"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data["count"], 0)

    def test_list_search_keyword_no_result(self) -> None:
        """키워드 검색 - 없는 키워드"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url, {"search_keyword": "없는키워드xyz"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_list_sort_created_at_asc(self) -> None:
        """생성일 오름차순 정렬"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url, {"sort": "created_at", "order": "asc"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        if len(results) >= 2:
            self.assertLessEqual(results[0]["created_at"], results[-1]["created_at"])

    def test_list_sort_created_at_desc(self) -> None:
        """생성일 내림차순 정렬"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url, {"sort": "created_at", "order": "desc"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        if len(results) >= 2:
            self.assertGreaterEqual(results[0]["created_at"], results[-1]["created_at"])

    def test_list_response_fields(self) -> None:
        """목록 응답 필드 확인"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)
        if response.data["results"]:
            result = response.data["results"][0]
            self.assertIn("id", result)
            self.assertIn("exam", result)
            self.assertIn("cohort", result)
            self.assertIn("status", result)
            self.assertIn("submit_count", result)
            self.assertIn("avg_score", result)


class TestDeploymentDetail(DeploymentBaseTestCase):
    """배포 상세 조회 테스트"""

    # 권한 테스트
    def test_admin_detail_success(self) -> None:
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.deployment.id)

    def test_user_detail_forbidden(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error_detail"), "쪽지시험 배포 상세 조회 권한이 없습니다.")

    def test_student_detail_forbidden(self) -> None:
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error_detail"), "쪽지시험 배포 상세 조회 권한이 없습니다.")

    def test_unauth_detail_unauthorized(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get("error_detail"), "자격 인증 데이터가 제공되지 않았습니다.")

    # 기능 실패 테스트
    def test_detail_invalid_path(self) -> None:
        """숫자가 아닌 deployment_id → 400"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error_detail"), "유효하지 않은 배포 상세 조회 요청입니다.")

    def test_detail_not_found(self) -> None:
        """존재하지 않는 deployment_id → 404"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.not_found_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error_detail"), "해당 배포 정보를 찾을 수 없습니다.")

    # 참가코드 테스트
    def test_detail_has_access_code(self) -> None:
        """상세 조회 응답에 참가코드 포함 확인"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_code", response.data)
        self.assertIsNotNone(response.data["access_code"])
        self.assertNotEqual(response.data["access_code"], "")

    def test_detail_access_code_matches_db(self) -> None:
        """응답의 참가코드가 DB 값과 일치하는지 확인"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["access_code"], self.deployment.access_code)

    def test_detail_has_exam_access_url(self) -> None:
        """상세 조회 응답에 시험 접근 URL 포함 확인"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("exam_access_url", response.data)

    def test_detail_response_fields(self) -> None:
        """상세 조회 응답 필드 전체 확인"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in [
            "id",
            "access_code",
            "exam_access_url",
            "cohort",
            "exam",
            "subject",
            "submit_count",
            "not_submitted_count",
            "duration_time",
            "open_at",
            "close_at",
            "created_at",
        ]:
            self.assertIn(field, response.data)


class TestDeploymentUpdate(DeploymentBaseTestCase):
    """배포 수정 테스트"""

    # 권한 테스트
    def test_admin_update_success(self) -> None:
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.detail_url, self.update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["deployment_id"], self.deployment.id)
        self.assertEqual(response.data["duration_time"], self.update_data["duration_time"])

    def test_user_update_forbidden(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.detail_url, self.update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error_detail"), "쪽지시험 배포 수정 권한이 없습니다.")

    def test_student_update_forbidden(self) -> None:
        self.client.force_authenticate(user=self.student)
        response = self.client.patch(self.detail_url, self.update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error_detail"), "쪽지시험 배포 수정 권한이 없습니다.")

    def test_unauth_update_unauthorized(self) -> None:
        response = self.client.patch(self.detail_url, self.update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get("error_detail"), "자격 인증 데이터가 제공되지 않았습니다.")

    # 기능 실패 테스트
    def test_update_invalid_path(self) -> None:
        """숫자가 아닌 deployment_id → 400"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.invalid_url, self.update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error_detail"), "유효하지 않은 배포 수정 요청입니다.")

    def test_update_invalid_open_at_past(self) -> None:
        """open_at이 과거 → 400"""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()
        data = {
            **self.update_data,
            "open_at": (now - timedelta(days=1)).isoformat(),
        }
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error_detail"), "유효하지 않은 배포 수정 요청입니다.")

    def test_update_invalid_close_at_past(self) -> None:
        """close_at이 과거인 경우 → 400"""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()
        data = {**self.update_data, "close_at": (now - timedelta(days=1)).isoformat()}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error_detail"), "유효하지 않은 배포 수정 요청입니다.")

    def test_update_invalid_close_before_open(self) -> None:
        """close_at이 open_at보다 이른 경우 → 400"""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()
        data = {
            "open_at": (now + timedelta(days=2)).isoformat(),
            "close_at": (now + timedelta(days=1)).isoformat(),
            "duration_time": 30,
        }
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error_detail"), "유효하지 않은 배포 수정 요청입니다.")

    def test_update_not_found(self) -> None:
        """존재하지 않는 deployment_id → 404"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.not_found_url, self.update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error_detail"), "수정할 배포 정보를 찾을 수 없습니다.")

    # 기능 성공 - DB 반영 확인
    def test_update_db_reflects_changes(self) -> None:
        """수정 후 DB에 반영되는지 확인"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.detail_url, self.update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.deployment.refresh_from_db()
        self.assertEqual(self.deployment.duration_time, self.update_data["duration_time"])

    def test_update_response_fields(self) -> None:
        """수정 응답 필드 확인"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.detail_url, self.update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in ["deployment_id", "duration_time", "open_at", "close_at", "updated_at"]:
            self.assertIn(field, response.data)


class TestDeploymentDelete(DeploymentBaseTestCase):
    """배포 삭제 테스트"""

    # 권한 테스트
    def test_user_delete_forbidden(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error_detail"), "배포 삭제 권한이 없습니다.")

    def test_student_delete_forbidden(self) -> None:
        self.client.force_authenticate(user=self.student)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error_detail"), "배포 삭제 권한이 없습니다.")

    def test_unauth_delete_unauthorized(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get("error_detail"), "자격 인증 데이터가 제공되지 않았습니다.")

    # 기능 실패 테스트
    def test_delete_invalid_path(self) -> None:
        """숫자가 아닌 deployment_id → 400"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.invalid_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error_detail"), "유효하지 않은 배포 삭제 요청입니다.")

    def test_delete_not_found(self) -> None:
        """존재하지 않는 deployment_id → 404"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.not_found_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error_detail"), "삭제할 배포 정보를 찾을 수 없습니다.")

    # 기능 성공 테스트
    def test_admin_delete_success(self) -> None:
        """삭제 성공 - 응답에 deployment_id 포함"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail2_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["deployment_id"], self.deployment2.id)

    def test_admin_delete_removes_from_db(self) -> None:
        """삭제 후 DB에서 제거됐는지 확인"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.delete(self.detail2_url)
        self.assertFalse(ExamDeployment.objects.filter(id=self.deployment2.id).exists())

    def test_delete_conflict(self) -> None:
        """락 충돌 발생 시 409 반환 확인 (mock - view 레벨)"""
        from apps.exams.exceptions.admin_exam_deployment_exception import (
            DeploymentDeleteConflictError,
        )

        self.client.force_authenticate(user=self.admin_user)
        with patch("apps.exams.views.admin_exam_deployment_view.delete_deployment") as mock_delete:
            mock_delete.side_effect = DeploymentDeleteConflictError()
            response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data.get("error_detail"), "배포 삭제 처리 중 충돌이 발생했습니다.")

    def test_delete_service_lock_conflict(self) -> None:
        """서비스 레벨 락 충돌 시 DeploymentDeleteConflictError 발생 확인 (mock - service 레벨)"""
        from django.db import OperationalError

        from apps.exams.exceptions.admin_exam_deployment_exception import (
            DeploymentDeleteConflictError,
        )
        from apps.exams.services.admin_exam_deployment_service import delete_deployment

        with patch("apps.exams.services.admin_exam_deployment_service.ExamDeployment.objects") as mock_objects:
            mock_qs = mock_objects.select_for_update.return_value
            mock_qs.get.side_effect = OperationalError("lock not available")
            with self.assertRaises(DeploymentDeleteConflictError):
                delete_deployment(self.deployment.id)


class TestDeploymentListInvalidRequest(DeploymentBaseTestCase):
    """배포 목록 조회 유효하지 않은 요청 테스트"""

    def test_list_invalid_sort_value(self) -> None:
        """잘못된 sort 값 → 400"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url, {"sort": "invalid_sort"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error_detail"), "유효하지 않은 조회 요청입니다.")


class TestDeploymentStatus(DeploymentBaseTestCase):
    """배포 상태 수정 테스트"""

    # 권한 테스트
    def test_admin_status_success(self) -> None:
        """어드민 상태 변경 성공"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.status_url, {"status": "Deactivated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_status_forbidden(self) -> None:
        """일반 유저 403"""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.status_url, {"status": "Deactivated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error_detail"), "쪽지시험 배포 상태 변경 권한이 없습니다.")

    def test_student_status_forbidden(self) -> None:
        """학생 403"""
        self.client.force_authenticate(user=self.student)
        response = self.client.patch(self.status_url, {"status": "Deactivated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error_detail"), "쪽지시험 배포 상태 변경 권한이 없습니다.")

    def test_unauth_status_unauthorized(self) -> None:
        """비로그인 401"""
        response = self.client.patch(self.status_url, {"status": "Deactivated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get("error_detail"), "자격 인증 데이터가 제공되지 않았습니다.")

    # 기능 실패 테스트
    def test_status_invalid_path(self) -> None:
        """숫자가 아닌 deployment_id → 400"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.status_invalid_url, {"status": "Deactivated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error_detail"), "유효하지 않은 배포 상태 요청입니다.")

    def test_status_invalid_value(self) -> None:
        """잘못된 status 값 → 400"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.status_url, {"status": "invalid_status"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error_detail"), "유효하지 않은 배포 상태 요청입니다.")

    def test_status_not_found(self) -> None:
        """존재하지 않는 deployment_id → 404"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.status_not_found_url, {"status": "Deactivated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error_detail"), "해당 배포 정보를 찾을 수 없습니다.")

    def test_status_conflict(self) -> None:
        """락 충돌 발생 시 409 반환 확인 (mock)"""
        from apps.exams.exceptions.admin_exam_deployment_exception import (
            DeploymentStatusConflictError,
        )

        self.client.force_authenticate(user=self.admin_user)
        with patch("apps.exams.views.admin_exam_deployment_view.update_deployment_status") as mock_update:
            mock_update.side_effect = DeploymentStatusConflictError()
            response = self.client.patch(self.status_url, {"status": "Deactivated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data.get("error_detail"), "배포 상태 변경 중 충돌이 발생했습니다.")

    # 기능 성공 테스트
    def test_status_response_fields(self) -> None:
        """응답 필드 확인"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.status_url, {"status": "Deactivated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("deployment_id", response.data)
        self.assertIn("status", response.data)

    def test_status_db_reflects_changes(self) -> None:
        """상태 변경 후 DB 반영 확인"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.status_url, {"status": "Deactivated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.deployment.refresh_from_db()
        self.assertEqual(self.deployment.status, "Deactivated")

    def test_status_activated(self) -> None:
        """Activated로 변경 확인"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.status_url, {"status": "Activated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "Activated")

from datetime import timedelta

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
from apps.exams.models.exam_submission_model import ExamSubmission
from apps.users.models import CohortStudents, User


class ExamDeploymentBaseTestCase(APITestCase):
    admin_user: User
    user: User
    student: User
    student_no_cohort: User
    course: Course
    subject: Subject
    exam: Exam
    cohort: Cohort
    cohort_not_open: Cohort
    cohort_expired: Cohort
    cohort_off: Cohort
    cohort_no_sub: Cohort
    cohort_answer: Cohort
    cohort_force: Cohort
    cohort_mc: Cohort
    deployment_active: ExamDeployment
    deployment_not_open: ExamDeployment
    deployment_expired: ExamDeployment
    deployment_off: ExamDeployment
    deployment_no_sub: ExamDeployment
    deployment_answer: ExamDeployment
    deployment_force: ExamDeployment
    deployment_mc: ExamDeployment
    submission: ExamSubmission
    submission_answer: ExamSubmission
    submission_force: ExamSubmission
    list_url: str
    check_code_active_url: str
    check_code_not_open_url: str
    check_code_expired_url: str
    check_code_not_found_url: str
    detail_active_url: str
    detail_expired_url: str
    detail_off_url: str
    detail_not_found_url: str
    detail_no_sub_url: str
    detail_answer_url: str
    detail_mc_url: str
    status_active_url: str
    status_not_open_url: str
    status_expired_url: str
    status_off_url: str
    status_not_found_url: str
    status_invalid_url: str
    status_force_url: str

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
        cls.student_no_cohort = User.objects.create_user(
            email="student2@test.com",
            name="student2",
            nickname="student2",
            phone_number="01044444444",
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
        cls.cohort_not_open = Cohort.objects.create(
            course=cls.course, number=2, max_student=30, start_date="2026-01-01", end_date="2026-06-30"
        )
        cls.cohort_expired = Cohort.objects.create(
            course=cls.course, number=3, max_student=30, start_date="2026-01-01", end_date="2026-06-30"
        )
        cls.cohort_off = Cohort.objects.create(
            course=cls.course, number=4, max_student=30, start_date="2026-01-01", end_date="2026-06-30"
        )
        cls.cohort_no_sub = Cohort.objects.create(
            course=cls.course, number=10, max_student=30, start_date="2026-01-01", end_date="2026-06-30"
        )
        cls.cohort_answer = Cohort.objects.create(
            course=cls.course, number=11, max_student=30, start_date="2026-01-01", end_date="2026-06-30"
        )
        cls.cohort_force = Cohort.objects.create(
            course=cls.course, number=20, max_student=30, start_date="2026-01-01", end_date="2026-06-30"
        )
        cls.cohort_mc = Cohort.objects.create(
            course=cls.course, number=21, max_student=30, start_date="2026-01-01", end_date="2026-06-30"
        )

        CohortStudents.objects.create(user=cls.student, cohort=cls.cohort)
        CohortStudents.objects.create(user=cls.student, cohort=cls.cohort_not_open)
        CohortStudents.objects.create(user=cls.student, cohort=cls.cohort_expired)
        CohortStudents.objects.create(user=cls.student, cohort=cls.cohort_off)
        CohortStudents.objects.create(user=cls.student, cohort=cls.cohort_no_sub)
        CohortStudents.objects.create(user=cls.student, cohort=cls.cohort_answer)
        CohortStudents.objects.create(user=cls.student, cohort=cls.cohort_force)
        CohortStudents.objects.create(user=cls.student, cohort=cls.cohort_mc)

        now = timezone.now()
        snapshot = [
            {
                "id": 1,
                "question": "테스트문제",
                "type": "short_answer",
                "point": 10,
                "prompt": None,
                "blank_count": None,
                "options_json": None,
            }
        ]
        snapshot_answer = [
            {
                "id": 99,
                "question": "답있는문제",
                "type": "short_answer",
                "point": 10,
                "prompt": None,
                "blank_count": None,
                "options_json": None,
            }
        ]
        snapshot_mc = [
            {
                "id": 2,
                "question": "객관식문제",
                "type": "multiple_choice",
                "point": 10,
                "prompt": None,
                "blank_count": None,
                "options_json": '["보기1", "보기2"]',
            }
        ]

        cls.deployment_active = ExamDeployment.objects.create(
            exam=cls.exam,
            cohort=cls.cohort,
            duration_time=60,
            open_at=now - timedelta(hours=1),
            close_at=now + timedelta(days=1),
            access_code="correctcode",
            questions_snapshot_json=snapshot,
            status=ExamDeployment.ExamStatus.ON,
        )
        cls.deployment_not_open = ExamDeployment.objects.create(
            exam=cls.exam,
            cohort=cls.cohort_not_open,
            duration_time=60,
            open_at=now + timedelta(days=1),
            close_at=now + timedelta(days=2),
            access_code="notopened1",
            questions_snapshot_json=snapshot,
            status=ExamDeployment.ExamStatus.ON,
        )
        cls.deployment_expired = ExamDeployment.objects.create(
            exam=cls.exam,
            cohort=cls.cohort_expired,
            duration_time=60,
            open_at=now - timedelta(days=2),
            close_at=now - timedelta(days=1),
            access_code="expiredco1",
            questions_snapshot_json=snapshot,
            status=ExamDeployment.ExamStatus.ON,
        )
        cls.deployment_off = ExamDeployment.objects.create(
            exam=cls.exam,
            cohort=cls.cohort_off,
            duration_time=60,
            open_at=now - timedelta(hours=1),
            close_at=now + timedelta(days=1),
            access_code="offcodexxx",
            questions_snapshot_json=snapshot,
            status=ExamDeployment.ExamStatus.OFF,
        )
        cls.deployment_no_sub = ExamDeployment.objects.create(
            exam=cls.exam,
            cohort=cls.cohort_no_sub,
            duration_time=60,
            open_at=now - timedelta(hours=1),
            close_at=now + timedelta(days=1),
            access_code="nosub12345",
            questions_snapshot_json=snapshot,
            status=ExamDeployment.ExamStatus.ON,
        )
        cls.deployment_answer = ExamDeployment.objects.create(
            exam=cls.exam,
            cohort=cls.cohort_answer,
            duration_time=60,
            open_at=now - timedelta(hours=1),
            close_at=now + timedelta(days=1),
            access_code="answerdep1",
            questions_snapshot_json=snapshot_answer,
            status=ExamDeployment.ExamStatus.ON,
        )
        cls.deployment_force = ExamDeployment.objects.create(
            exam=cls.exam,
            cohort=cls.cohort_force,
            duration_time=1,
            open_at=now - timedelta(hours=2),
            close_at=now + timedelta(days=1),
            access_code="forcecode1",
            questions_snapshot_json=snapshot,
            status=ExamDeployment.ExamStatus.ON,
        )
        cls.deployment_mc = ExamDeployment.objects.create(
            exam=cls.exam,
            cohort=cls.cohort_mc,
            duration_time=60,
            open_at=now - timedelta(hours=1),
            close_at=now + timedelta(days=1),
            access_code="mccodexxx1",
            questions_snapshot_json=snapshot_mc,
            status=ExamDeployment.ExamStatus.ON,
        )

        cls.submission = ExamSubmission.objects.create(
            deployment=cls.deployment_active,
            submitter=cls.student,
            started_at=now - timedelta(minutes=10),
            score=80,
            correct_answer_count=8,
        )
        cls.submission_answer = ExamSubmission.objects.create(
            deployment=cls.deployment_answer,
            submitter=cls.student,
            started_at=now - timedelta(minutes=5),
            answer_json={"99": "테스트답변"},
        )
        cls.submission_force = ExamSubmission.objects.create(
            deployment=cls.deployment_force,
            submitter=cls.student,
            started_at=now - timedelta(hours=2),
        )

        cls.list_url = reverse("deployment")
        cls.check_code_active_url = reverse("deployment-code", kwargs={"deployment_id": cls.deployment_active.id})
        cls.check_code_not_open_url = reverse("deployment-code", kwargs={"deployment_id": cls.deployment_not_open.id})
        cls.check_code_expired_url = reverse("deployment-code", kwargs={"deployment_id": cls.deployment_expired.id})
        cls.check_code_not_found_url = reverse("deployment-code", kwargs={"deployment_id": 99999})
        cls.detail_active_url = reverse("deployment-detail", kwargs={"deployment_id": cls.deployment_active.id})
        cls.detail_expired_url = reverse("deployment-detail", kwargs={"deployment_id": cls.deployment_expired.id})
        cls.detail_off_url = reverse("deployment-detail", kwargs={"deployment_id": cls.deployment_off.id})
        cls.detail_not_found_url = reverse("deployment-detail", kwargs={"deployment_id": 99999})
        cls.detail_no_sub_url = reverse("deployment-detail", kwargs={"deployment_id": cls.deployment_no_sub.id})
        cls.detail_answer_url = reverse("deployment-detail", kwargs={"deployment_id": cls.deployment_answer.id})
        cls.detail_mc_url = reverse("deployment-detail", kwargs={"deployment_id": cls.deployment_mc.id})
        cls.status_active_url = reverse("deployment-status", kwargs={"deployment_id": cls.deployment_active.id})
        cls.status_not_open_url = reverse("deployment-status", kwargs={"deployment_id": cls.deployment_not_open.id})
        cls.status_expired_url = reverse("deployment-status", kwargs={"deployment_id": cls.deployment_expired.id})
        cls.status_off_url = reverse("deployment-status", kwargs={"deployment_id": cls.deployment_off.id})
        cls.status_not_found_url = reverse("deployment-status", kwargs={"deployment_id": 99999})
        cls.status_invalid_url = reverse("deployment-status", kwargs={"deployment_id": 0})
        cls.status_force_url = reverse("deployment-status", kwargs={"deployment_id": cls.deployment_force.id})

    def setUp(self) -> None:
        self.client = APIClient()


class TestExamDeploymentList(ExamDeploymentBaseTestCase):
    """쪽지시험 배포 목록 조회 테스트"""

    # 권한 테스트
    def test_student_list_success(self) -> None:
        """학생 200"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_list_forbidden(self) -> None:
        """일반 유저 403"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error_detail"), "권한이 없습니다.")

    def test_admin_list_not_in_cohort_404(self) -> None:
        """어드민은 권한 통과하지만 기수 미등록 → 404"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error_detail"), "사용자 정보를 찾을 수 없습니다.")

    def test_unauth_list_unauthorized(self) -> None:
        """비로그인 401"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get("error_detail"), "자격 인증 데이터가 제공되지 않았습니다.")

    # 기능 실패 테스트
    def test_list_student_not_in_cohort_404(self) -> None:
        """기수에 속하지 않은 학생 → 404"""
        self.client.force_authenticate(user=self.student_no_cohort)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error_detail"), "사용자 정보를 찾을 수 없습니다.")

    # 기능 성공 테스트
    def test_list_returns_only_on_status(self) -> None:
        """status=ON인 배포만 반환 (OFF 배포 미포함)"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result_ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.deployment_off.id, result_ids)

    def test_list_filter_all(self) -> None:
        """status=all → 제출/미제출 모두 반환"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.list_url, {"status": "all"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result_ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.deployment_active.id, result_ids)

    def test_list_filter_done(self) -> None:
        """status=done → 제출한 배포만 반환"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.list_url, {"status": "done"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data["results"]:
            self.assertTrue(item["is_done"])

    def test_list_filter_pending(self) -> None:
        """status=pending → 미제출 배포만 반환"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.list_url, {"status": "pending"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data["results"]:
            self.assertFalse(item["is_done"])

    def test_list_done_submission_id_not_null(self) -> None:
        """제출 완료 항목 submission_id는 null이 아님"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.list_url, {"status": "done"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data["results"]:
            self.assertIsNotNone(item["submission_id"])

    def test_list_pending_submission_id_null(self) -> None:
        """미제출 항목 submission_id는 null"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.list_url, {"status": "pending"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data["results"]:
            self.assertIsNone(item["submission_id"])

    def test_list_done_exam_info_has_score(self) -> None:
        """제출 완료 항목 exam_info.score가 null이 아님"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.list_url, {"status": "done"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data["results"]:
            self.assertEqual(item["exam_info"]["status"], "done")
            self.assertIsNotNone(item["exam_info"]["score"])

    def test_list_pending_exam_info_score_null(self) -> None:
        """미제출 항목 exam_info.score는 null"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.list_url, {"status": "pending"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data["results"]:
            self.assertEqual(item["exam_info"]["status"], "pending")
            self.assertIsNone(item["exam_info"]["score"])

    def test_list_response_fields(self) -> None:
        """응답 필드 확인 (page, has_next, results)"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("page", response.data)
        self.assertIn("has_next", response.data)
        self.assertIn("results", response.data)
        if response.data["results"]:
            result = response.data["results"][0]
            for field in [
                "id",
                "submission_id",
                "exam",
                "question_count",
                "total_score",
                "exam_info",
                "is_done",
                "duration_time",
            ]:
                self.assertIn(field, result)

    def test_list_pagination_has_next_false(self) -> None:
        """결과가 page_size 이하 → has_next=False"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["has_next"])

    def test_list_done_correct_answer_count_not_null(self) -> None:
        """제출 완료 항목 exam_info.correct_answer_count가 null이 아님"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.list_url, {"status": "done"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data["results"]:
            self.assertIsNotNone(item["exam_info"]["correct_answer_count"])

    def test_list_pending_correct_answer_count_null(self) -> None:
        """미제출 항목 exam_info.correct_answer_count는 null"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.list_url, {"status": "pending"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data["results"]:
            self.assertIsNone(item["exam_info"]["correct_answer_count"])

    def test_list_question_count_value(self) -> None:
        """question_count가 snapshot 문제 수와 일치"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.list_url, {"status": "done"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        done_item = next((item for item in response.data["results"] if item["id"] == self.deployment_active.id), None)
        assert done_item is not None
        self.assertEqual(done_item["question_count"], len(self.deployment_active.questions_snapshot_json))

    def test_list_total_score_value(self) -> None:
        """total_score가 snapshot point 합산과 일치"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.list_url, {"status": "done"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        done_item = next((item for item in response.data["results"] if item["id"] == self.deployment_active.id), None)
        assert done_item is not None
        expected_total = sum(q.get("point", 0) for q in self.deployment_active.questions_snapshot_json)
        self.assertEqual(done_item["total_score"], expected_total)

    def test_list_exam_nested_fields(self) -> None:
        """exam 중첩 필드 구조 확인 (subject 포함)"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if response.data["results"]:
            exam = response.data["results"][0]["exam"]
            for field in ["id", "title", "thumbnail_img_url", "subject"]:
                self.assertIn(field, exam)
            for field in ["id", "title", "thumbnail_img_url"]:
                self.assertIn(field, exam["subject"])


class TestExamDeploymentCheckCode(ExamDeploymentBaseTestCase):
    """쪽지시험 응시 코드 확인 테스트"""

    # 권한 테스트
    def test_student_check_success(self) -> None:
        """학생 204"""
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.check_code_active_url, {"code": "correctcode"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_check_forbidden(self) -> None:
        """일반 유저 403"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.check_code_active_url, {"code": "correctcode"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error_detail"), "시험에 응시할 권한이 없습니다.")

    def test_admin_check_not_in_cohort_404(self) -> None:
        """어드민은 권한 통과하지만 기수 미등록 → 404"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.check_code_active_url, {"code": "correctcode"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error_detail"), "배포 정보를 찾을 수 없습니다.")

    def test_unauth_check_unauthorized(self) -> None:
        """비로그인 401"""
        response = self.client.post(self.check_code_active_url, {"code": "correctcode"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get("error_detail"), "자격 인증 데이터가 제공되지 않았습니다.")

    # 기능 실패 테스트
    def test_check_wrong_code_400(self) -> None:
        """틀린 코드 → 400"""
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.check_code_active_url, {"code": "wrongcode"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error_detail"), "응시 코드가 일치하지 않습니다.")

    def test_check_empty_code_400(self) -> None:
        """코드 미입력 → 400"""
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.check_code_active_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error_detail"), "응시 코드가 일치하지 않습니다.")

    def test_check_not_yet_open_423(self) -> None:
        """아직 오픈 안 된 시험 → 423"""
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.check_code_not_open_url, {"code": "notopened1"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_423_LOCKED)
        self.assertEqual(response.data.get("error_detail"), "아직 응시할 수 없습니다.")

    def test_check_not_found_404(self) -> None:
        """존재하지 않는 deployment_id → 404"""
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.check_code_not_found_url, {"code": "anycode"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error_detail"), "배포 정보를 찾을 수 없습니다.")

    def test_check_student_not_in_cohort_404(self) -> None:
        """해당 기수 소속이 아닌 학생 → 404"""
        self.client.force_authenticate(user=self.student_no_cohort)
        response = self.client.post(self.check_code_active_url, {"code": "correctcode"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error_detail"), "배포 정보를 찾을 수 없습니다.")

    # 기능 성공 테스트
    def test_check_success_no_body(self) -> None:
        """코드 일치 → 204 응답 바디 없음"""
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.check_code_active_url, {"code": "correctcode"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(response.content)

    def test_check_expired_correct_code_423(self) -> None:
        """만료된 시험 코드 입력 시 423"""
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.check_code_expired_url, {"code": "expiredco1"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_423_LOCKED)
        self.assertEqual(response.data.get("error_detail"), "시험이 종료되었습니다.")


class TestExamDeploymentDetail(ExamDeploymentBaseTestCase):
    """쪽지시험 문제 조회 테스트"""

    # 권한 테스트
    def test_student_detail_success(self) -> None:
        """학생 200"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.detail_active_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_detail_forbidden(self) -> None:
        """일반 유저 403"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_active_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error_detail"), "권한이 없습니다.")

    def test_admin_detail_not_in_cohort_404(self) -> None:
        """어드민은 권한 통과하지만 기수 미등록 → 404"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.detail_active_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error_detail"), "해당 시험 정보를 찾을 수 없습니다.")

    def test_unauth_detail_unauthorized(self) -> None:
        """비로그인 401"""
        response = self.client.get(self.detail_active_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get("error_detail"), "자격 인증 데이터가 제공되지 않았습니다.")

    # 기능 실패 테스트
    def test_detail_not_found_404(self) -> None:
        """존재하지 않는 deployment_id → 404"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.detail_not_found_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error_detail"), "해당 시험 정보를 찾을 수 없습니다.")

    def test_detail_student_not_in_cohort_404(self) -> None:
        """해당 기수 소속이 아닌 학생 → 404"""
        self.client.force_authenticate(user=self.student_no_cohort)
        response = self.client.get(self.detail_active_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error_detail"), "해당 시험 정보를 찾을 수 없습니다.")

    def test_detail_expired_410(self) -> None:
        """종료된 시험(close_at 지남) → 410"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.detail_expired_url)
        self.assertEqual(response.status_code, status.HTTP_410_GONE)
        self.assertEqual(response.data.get("error_detail"), "시험이 종료되었습니다.")

    def test_detail_off_status_410(self) -> None:
        """비활성화(status=OFF) 시험 → 410"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.detail_off_url)
        self.assertEqual(response.status_code, status.HTTP_410_GONE)
        self.assertEqual(response.data.get("error_detail"), "시험이 종료되었습니다.")

    # 기능 성공 테스트
    def test_detail_response_fields(self) -> None:
        """응답 필드 확인"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.detail_active_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in ["exam_id", "exam_title", "duration_time", "elapsed_time", "cheating_count", "questions"]:
            self.assertIn(field, response.data)

    def test_detail_questions_have_number(self) -> None:
        """문제에 number 필드가 1부터 순서대로 포함"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.detail_active_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i, question in enumerate(response.data["questions"]):
            self.assertEqual(question["number"], i + 1)

    def test_detail_elapsed_time_with_submission(self) -> None:
        """제출 기록 있으면 elapsed_time > 0"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.detail_active_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data["elapsed_time"], 0)

    def test_detail_elapsed_time_without_submission(self) -> None:
        """제출 기록 없으면 elapsed_time = 0"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.detail_no_sub_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["elapsed_time"], 0)

    def test_detail_answer_input_in_questions(self) -> None:
        """문제에 answer_input 필드 포함"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.detail_active_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for question in response.data["questions"]:
            self.assertIn("answer_input", question)

    def test_detail_cheating_count_default(self) -> None:
        """제출 기록 있을 때 cheating_count 반환"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.detail_active_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("cheating_count", response.data)
        self.assertEqual(response.data["cheating_count"], self.submission.cheating_count)

    def test_detail_question_fields_structure(self) -> None:
        """문제 필드 구조 상세 확인"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.detail_active_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data["questions"]) > 0)
        question = response.data["questions"][0]
        for field in [
            "question_id",
            "number",
            "type",
            "question",
            "point",
            "prompt",
            "blank_count",
            "options",
            "answer_input",
        ]:
            self.assertIn(field, question)

    def test_detail_answer_input_null_when_no_answer(self) -> None:
        """answer_json에 해당 문제 답 없으면 answer_input=null"""
        self.client.force_authenticate(user=self.student)
        # submission의 answer_json이 기본값 {} 이므로 answer_input은 null
        response = self.client.get(self.detail_active_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for question in response.data["questions"]:
            self.assertIsNone(question["answer_input"])

    def test_detail_answer_input_value_when_answered(self) -> None:
        """answer_json에 해당 문제 답 있으면 answer_input에 값 반환"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.detail_answer_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["questions"][0]["answer_input"], "테스트답변")

    def test_detail_options_json_parsed(self) -> None:
        """options_json이 있는 문제는 options가 파싱된 문자열 리스트로 반환"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.detail_mc_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        options = response.data["questions"][0]["options"]
        self.assertIsNotNone(options)
        self.assertIsInstance(options, list)
        self.assertEqual(len(options), 2)
        self.assertIsInstance(options[0], str)


class TestExamDeploymentStatus(ExamDeploymentBaseTestCase):
    """쪽지시험 상태 조회 테스트"""

    # 권한 테스트
    def test_student_status_success(self) -> None:
        """학생 200"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.status_active_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_status_forbidden(self) -> None:
        """일반 유저 403"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.status_active_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error_detail"), "권한이 없습니다.")

    def test_admin_status_not_in_cohort_404(self) -> None:
        """어드민은 권한 통과하지만 기수 미등록 → 404"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.status_active_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error_detail"), "해당 시험 정보를 찾을 수 없습니다.")

    def test_unauth_status_unauthorized(self) -> None:
        """비로그인 401"""
        response = self.client.get(self.status_active_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get("error_detail"), "자격 인증 데이터가 제공되지 않았습니다.")

    # 기능 실패 테스트
    def test_status_invalid_path_400(self) -> None:
        """deployment_id=0 (min_value=1 위반) → 400"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.status_invalid_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error_detail"), "유효하지 않은 시험 응시 세션입니다.")

    def test_status_not_found_404(self) -> None:
        """존재하지 않는 deployment_id → 404"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.status_not_found_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error_detail"), "해당 시험 정보를 찾을 수 없습니다.")

    def test_status_student_not_in_cohort_404(self) -> None:
        """해당 기수 소속이 아닌 학생 → 404"""
        self.client.force_authenticate(user=self.student_no_cohort)
        response = self.client.get(self.status_active_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error_detail"), "해당 시험 정보를 찾을 수 없습니다.")

    def test_status_expired_200_closed(self) -> None:
        """종료된 시험(close_at 지남) → 200 closed"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.status_expired_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("exam_status"), "closed")
        self.assertTrue(response.data.get("force_submit"))

    def test_status_off_200_closed(self) -> None:
        """비활성화(status=OFF) 시험 → 200 closed"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.status_off_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("exam_status"), "closed")
        self.assertTrue(response.data.get("force_submit"))

    # 기능 성공 테스트
    def test_status_response_fields(self) -> None:
        """응답 필드 확인"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.status_active_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("exam_status", response.data)
        self.assertIn("force_submit", response.data)

    def test_status_activated_value(self) -> None:
        """활성화 시험 exam_status = 'activated'"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.status_active_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["exam_status"], "activated")

    def test_status_force_submit_false(self) -> None:
        """제한 시간 내 → force_submit=False"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.status_active_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["force_submit"])

    def test_status_force_submit_true(self) -> None:
        """제한 시간 초과 → force_submit=True"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.status_force_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["force_submit"])

    def test_status_force_submit_false_no_submission(self) -> None:
        """제출 기록 없으면 force_submit=False"""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.status_not_open_url)
        # deployment_not_open은 close_at이 미래이고 status=ON이므로 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["force_submit"])

from __future__ import annotations

from datetime import timedelta
from typing import Any, ClassVar

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.courses.models.cohort import Cohort
from apps.courses.models.course import Course
from apps.users.models import CohortStudents, TrainigAssistants, User, Withdrawal


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


def create_admin(
    email: str = "admin@oz.com",
    nickname: str = "관리자",
    phone_number: str = "01099998888",
) -> User:
    return create_user(
        email=email,
        nickname=nickname,
        phone_number=phone_number,
        role=User.Role.ADMIN,
    )


def get_auth_header(user: User) -> dict[str, Any]:
    token = RefreshToken.for_user(user)
    return {"HTTP_AUTHORIZATION": f"Bearer {str(token.access_token)}"}


def create_withdrawal(user: User) -> Withdrawal:
    user.is_active = False
    user.save(update_fields=["is_active"])
    return Withdrawal.objects.create(
        user=user,
        reason=Withdrawal.Reason.NO_LONGER_NEEDED,
        reason_detail="테스트 탈퇴",
        due_date=timezone.localdate() + timedelta(weeks=2),
    )


def create_course_and_cohort() -> tuple[Course, Cohort]:
    course = Course.objects.create(name="초격차 백엔드 부트캠프", tag="BE")
    cohort = Cohort.objects.create(
        course=course,
        number=1,
        max_student=30,
        start_date=timezone.localdate(),
        end_date=timezone.localdate() + timedelta(weeks=24),
    )
    return course, cohort


class AdminWithdrawalListViewGetTest(APITestCase):
    """GET /api/v1/admin/withdrawals 탈퇴 목록 조회"""

    url_name: ClassVar[str] = "admin-withdrawal-list"

    def setUp(self) -> None:
        self.admin = create_admin()
        self.user = create_user(
            email="student@oz.com",
            nickname="수강생",
            phone_number="01022223333",
            role=User.Role.STUDENT,
        )
        self.user.gender = User.Gender.MALE
        self.user.profile_img_url = "https://example.com/images/profiles/image.png"
        self.user.save(update_fields=["gender", "profile_img_url"])
        self.other_user = create_user(email="other@oz.com", nickname="기타유저", phone_number="01033334444")
        _, self.cohort = create_course_and_cohort()
        CohortStudents.objects.create(user=self.user, cohort=self.cohort)
        self.withdrawal = create_withdrawal(self.user)
        self.other_withdrawal = create_withdrawal(self.other_user)
        self.auth = get_auth_header(self.admin)
        self.url = reverse(self.url_name)

    def test_admin_can_retrieve_withdrawal_list(self) -> None:
        self.assertEqual(self.url, "/api/v1/admin/withdrawals")
        response = self.client.get(self.url, **self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 2)
        self.assertIn("next", data)
        self.assertIn("previous", data)
        self.assertEqual(len(data["results"]), 2)
        self.assertIn("reason_display", data["results"][0])
        self.assertIn("withdrawn_at", data["results"][0])
        self.assertEqual(data["results"][0]["reason_display"], "더 이상 필요하지 않음")
        student_result = next(result for result in data["results"] if result["id"] == self.withdrawal.id)
        self.assertEqual(
            set(student_result["user"].keys()),
            {"id", "email", "name", "role", "position", "birthday"},
        )
        self.assertEqual(student_result["user"]["position"], "ENROLLED")

    def test_admin_can_filter_withdrawal_list_by_search_and_role(self) -> None:
        response = self.client.get(self.url, {"search": "student", "role": User.Role.STUDENT}, **self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["id"], self.withdrawal.id)

    def test_admin_can_filter_withdrawal_list_by_position(self) -> None:
        ta_user = create_user(
            email="ta@oz.com",
            nickname="조교",
            phone_number="01055556666",
        )
        ta_withdrawal = create_withdrawal(ta_user)
        TrainigAssistants.objects.create(user=ta_user, cohort=self.cohort)

        response = self.client.get(self.url, {"position": "TA"}, **self.auth)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["id"], ta_withdrawal.id)
        self.assertEqual(data["results"][0]["user"]["position"], "TA")

    def test_admin_can_control_page_size(self) -> None:
        response = self.client.get(self.url, {"page_size": 1}, **self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 2)
        self.assertEqual(len(data["results"]), 1)

    def test_returns_400_for_invalid_query_params(self) -> None:
        response = self.client.get(self.url, {"page": 0}, **self.auth)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("page", response.json()["error_detail"])

    def test_excludes_withdrawal_without_user(self) -> None:
        Withdrawal.objects.create(
            user=None,
            reason=Withdrawal.Reason.OTHER,
            reason_detail="유저 삭제됨",
            due_date=timezone.localdate() + timedelta(weeks=2),
        )
        response = self.client.get(self.url, **self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 2)

    def test_returns_401_without_token(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_403_for_non_admin(self) -> None:
        normal_user = create_user(email="normal@oz.com", nickname="일반유저", phone_number="01044445555")
        auth = get_auth_header(normal_user)
        response = self.client.get(self.url, **auth)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminWithdrawalDetailViewTest(APITestCase):
    """GET/DELETE /api/v1/admin/withdrawals/{withdrawal_id} 탈퇴 상세/취소"""

    url_name: ClassVar[str] = "admin-withdrawal-detail"

    def setUp(self) -> None:
        self.admin = create_admin()
        self.user = create_user(
            email="detail@oz.com",
            nickname="상세유저",
            phone_number="01066667777",
            role=User.Role.STUDENT,
        )
        self.user.gender = User.Gender.MALE
        self.user.profile_img_url = "https://example.com/images/profiles/image.png"
        self.user.save(update_fields=["gender", "profile_img_url"])
        _, self.cohort = create_course_and_cohort()
        CohortStudents.objects.create(user=self.user, cohort=self.cohort)
        self.withdrawal = create_withdrawal(self.user)
        self.auth = get_auth_header(self.admin)
        self.url = reverse(self.url_name, kwargs={"withdrawal_id": self.withdrawal.id})

    def test_admin_can_retrieve_withdrawal_detail(self) -> None:
        response = self.client.get(self.url, **self.auth)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["id"], self.withdrawal.id)
        self.assertEqual(data["user"]["id"], self.user.id)
        self.assertEqual(data["user"]["email"], self.user.email)
        self.assertEqual(data["user"]["nickname"], self.user.nickname)
        self.assertEqual(data["user"]["name"], self.user.name)
        self.assertEqual(data["user"]["gender"], "M")
        self.assertEqual(data["user"]["role"], "STUDENT")
        self.assertEqual(data["user"]["position"], "ENROLLED")
        self.assertEqual(data["user"]["status"], "WITHDREW")
        self.assertEqual(data["user"]["profile_img_url"], "https://example.com/images/profiles/image.png")
        self.assertIn("created_at", data["user"])
        self.assertEqual(data["reason"], "NO_LONGER_NEEDED")
        self.assertEqual(data["reason_display"], "더 이상 필요하지 않음")
        self.assertEqual(data["reason_detail"], "테스트 탈퇴")
        self.assertEqual(data["due_date"], str(self.withdrawal.due_date))
        self.assertIn("withdrawn_at", data)
        self.assertEqual(len(data["assigned_courses"]), 1)
        assigned_course = data["assigned_courses"][0]
        self.assertEqual(assigned_course["course"]["id"], self.cohort.course.id)
        self.assertEqual(assigned_course["course"]["name"], self.cohort.course.name)
        self.assertEqual(assigned_course["course"]["tag"], self.cohort.course.tag)
        self.assertEqual(assigned_course["cohort"]["id"], self.cohort.id)
        self.assertEqual(assigned_course["cohort"]["number"], self.cohort.number)
        self.assertEqual(assigned_course["cohort"]["status"], self.cohort.status)
        self.assertEqual(assigned_course["cohort"]["start_date"], str(self.cohort.start_date))
        self.assertEqual(assigned_course["cohort"]["end_date"], str(self.cohort.end_date))

    def test_withdrawal_detail_not_found_returns_404(self) -> None:
        url = reverse(self.url_name, kwargs={"withdrawal_id": self.withdrawal.id + 999})

        response = self.client.get(url, **self.auth)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], "회원탈퇴 정보를 찾을 수 없습니다.")

    def test_admin_can_cancel_withdrawal(self) -> None:
        response = self.client.delete(self.url, **self.auth)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["detail"], "회원 탈퇴 취소처리 완료.")
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertFalse(Withdrawal.objects.filter(id=self.withdrawal.id).exists())

    def test_cancel_withdrawal_not_found_returns_404(self) -> None:
        url = reverse(self.url_name, kwargs={"withdrawal_id": self.withdrawal.id + 999})

        response = self.client.delete(url, **self.auth)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], "회원탈퇴 정보를 찾을 수 없습니다.")

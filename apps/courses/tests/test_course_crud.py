from __future__ import annotations

import itertools
from typing import Any

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.courses.models.course import Course
from apps.users.models import User

_counter = itertools.count(1)


def make_user(**kwargs: Any) -> User:
    n = next(_counter)
    defaults: dict[str, Any] = {
        "email": f"testuser{n}@test.com",
        "nickname": f"유저{n}",
        "name": "이름",
        "phone_number": f"010{n:08d}",
        "role": "USER",
        "is_active": True,
    }
    defaults.update(kwargs)
    user = User(**defaults)
    user.set_unusable_password()
    user.save()
    return user


class CourseCrudTestBase(APITestCase):
    admin: User
    normal_user: User
    course: Course

    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin = make_user(role="ADMIN")
        cls.normal_user = make_user(role="USER")
        cls.course = Course.objects.create(
            name="테스트 과정",
            tag="TST",
            description="설명",
            thumbnail_img_url="https://test.com/img.png",
        )

    def setUp(self) -> None:
        self.client = APIClient()


# ----- 과정 리스트 조회 -----
class CourseListViewTest(CourseCrudTestBase):
    def test_admin_can_list_courses(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/v1/course/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self) -> None:
        response = self.client.get("/api/v1/course/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")

    def test_normal_user_returns_403(self) -> None:
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get("/api/v1/course/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "관리자 권한이 필요합니다.")


# ----- 과정 등록 -----
class AdminCourseCreateViewTest(CourseCrudTestBase):
    def test_admin_can_create_course(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            "/api/v1/admin/courses/",
            data={"name": "신규 과정", "tag": "NEW", "description": "설명", "thumbnail_img_url": "https://t.com/n.png"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_name_returns_409(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            "/api/v1/admin/courses/",
            data={"name": "테스트 과정", "tag": "DUP"},  # 이미 setUpTestData에 있음
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_invalid_request_returns_400(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/api/v1/admin/courses/", data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_returns_401(self) -> None:
        response = self.client.post("/api/v1/admin/courses/", data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_normal_user_returns_403(self) -> None:
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post("/api/v1/admin/courses/", data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# ----- 과정 상세 조회 / 수정 / 삭제 -----
class AdminCourseDetailViewTest(CourseCrudTestBase):
    def test_admin_can_get_detail(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f"/api/v1/admin/courses/{self.course.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_not_found_returns_404(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/v1/admin/courses/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "해당 과정을 찾을 수 없습니다.")

    def test_get_unauthenticated_returns_401_with_login_message(self) -> None:
        response = self.client.get(f"/api/v1/admin/courses/{self.course.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "로그인이 필요합니다.")

    def test_admin_can_patch(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f"/api/v1/admin/courses/{self.course.id}/",
            data={"name": "수정된 과정"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_not_found_returns_404(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch("/api/v1/admin/courses/99999/", data={"name": "x"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_normal_user_returns_403_with_no_permission_message(self) -> None:
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.patch(f"/api/v1/admin/courses/{self.course.id}/", data={"name": "x"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "권한이 없습니다.")

    def test_admin_can_delete(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f"/api/v1/admin/courses/{self.course.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_not_found_returns_404(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete("/api/v1/admin/courses/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

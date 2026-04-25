import re

from rest_framework.test import APITestCase
from apps.users.models import User
from django.urls import reverse
from unittest.mock import patch

class PresignedUrlBaseTestCase(APITestCase):
    user: User
    admin: User

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
        cls.no_name = '.jpg'
        cls.no_subfix = "test_file"
        cls.file_name = "test_file.jpg"


class TestPresignedUrl(PresignedUrlBaseTestCase):
    def setUp(self):
        self.mock_s3 = patch("apps.core.utils.s3_urls.s3.s3").start()
        self.mock_s3.generate_presigned_url.return_value = "https://test-presigned-url.com"

    def tearDown(self):
        patch.stopall()

    # 권한
    def test_presigned_url_as_admin(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(reverse("presigned-url"), {"file_name": self.file_name})

        self.assertEqual(response.status_code, 200)
        self.assertIn("presigned_url", response.data)
        self.assertIn("img_url", response.data)
        self.assertIn("key", response.data)

        # key값
        key = response.data["key"]
        self.assertTrue(key.startswith("uploads/exams/thumbnails/"))
        self.assertTrue(key.endswith(".jpg"))

        # uuid 값
        uuid_part = key.removeprefix("uploads/exams/thumbnails/").removesuffix(".jpg")
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
        self.assertRegex(uuid_part, uuid_pattern)

    def test_presigned_url_as_user(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse("presigned-url"), {"file_name": self.file_name})

        self.assertEqual(response.status_code, 403)

    def test_presigned_url_as_anonymous(self) -> None:
        response = self.client.put(reverse("presigned-url"), {"file_name": self.file_name})

        self.assertEqual(response.status_code, 401)

    # 파일 관련 에러 검증
    def test_presigned_url_no_name(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(reverse("presigned-url"), {"file_name": self.no_name})

        self.assertEqual(response.status_code, 400)

    def test_presigned_url_no_subfix(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(reverse("presigned-url"), {"file_name": self.no_subfix})

        self.assertEqual(response.status_code, 400)

    def test_presigned_url_invalid_subfix(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(reverse("presigned-url"), {"file_name": "test_file.test"})

        self.assertEqual(response.status_code, 400)

    def test_presigned_url_no_file(self) -> None:
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(reverse("presigned-url"))

        self.assertEqual(response.status_code, 400)


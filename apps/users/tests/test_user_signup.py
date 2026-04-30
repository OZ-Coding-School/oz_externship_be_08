import uuid

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status

from apps.core.utils.isolated_cache_testcase import IsolatedRedisTestClient
from apps.users.utils.purpose_enum import AuthPurpose, SmsPurpose

User = get_user_model()


class SignupViewTest(IsolatedRedisTestClient):
    def setUp(self) -> None:
        super().setUp()

        self.url = reverse("users:signup")

        self.email_token = f"email_{uuid.uuid4().hex}"
        self.sms_token = f"sms_{uuid.uuid4().hex}"

        self.email = f"test_{uuid.uuid4()}@example.com"
        self.phone_number = f"010{str(uuid.uuid4().int)[:8]}"
        self.nickname = f"u{uuid.uuid4().hex[:7]}"

        self.valid_payload = {
            "password": "Password1234@",
            "nickname": self.nickname,
            "name": "테스터",
            "birthday": "2000-11-11",
            "gender": "M",
            "email_token": self.email_token,
            "sms_token": self.sms_token,
        }

        self.email_key = f"email_verify_token_{self.email_token}"
        self.sms_key = f"sms_verify_token_{self.sms_token}"

    def tearDown(self) -> None:
        """DB와 Redis 캐시를 모두 초기화하여 다음 테스트에 영향을 주지 않게 합니다."""
        User.objects.all().delete()
        cache.clear()  # 🧹 레디스 찌꺼기 완벽 청소
        super().tearDown()

    def set_cache_data(self) -> None:
        """테스트를 위해 Redis 캐시에 인증 데이터를 주입합니다."""
        cache.set(self.email_key, {"email": self.email, "purpose": AuthPurpose.SIGNUP.value}, timeout=300)

        cache.set(self.sms_key, {"phone_number": self.phone_number, "purpose": SmsPurpose.SIGNUP.value}, timeout=300)

    def test_signup_success(self) -> None:
        """정상적인 데이터로 회원가입 성공 (201) 테스트"""
        self.set_cache_data()

        response = self.client.post(self.url, self.valid_payload, format="json")
        # 상태 코드 201과 응답 메시지 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], "회원가입이 완료되었습니다.")

    def test_signup_missing_fields(self) -> None:
        """필수 필드(nickname) 누락 시 400 에러 반환 테스트"""
        invalid_payload = self.valid_payload.copy()
        # 고의로 닉네임 필드를 제거하여 잘못된 요청
        invalid_payload.pop("nickname")

        response = self.client.post(self.url, data=invalid_payload, format="json")

        # 상태 코드가 400인지 검증
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # error_detail 내에 에러가 발생한 필드(nickname)가 명시되어 있는지 확인
        self.assertIn("error_detail", response.data)
        self.assertIn("nickname", response.data["error_detail"])

    def test_signup_conflict(self) -> None:
        """중복 가입 시도 시 409 Conflict 반환 테스트"""

        # 정상적으로 회원가입을 1회 진행하여 DB에 유저를 생성
        self.set_cache_data()

        self.client.post(self.url, data=self.valid_payload, format="json")

        # 완전히 동일한 데이터로 다시 한번 가입을 시도
        # Serializer의 유니크 제약조건 등에 의해 ValidationError가 발생
        self.set_cache_data()

        response = self.client.post(self.url, data=self.valid_payload, format="json")

        # 상태 코드 409 반환을 검증
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("error_detail", response.data)

from django.core.cache import cache
from django.urls import reverse
from rest_framework import status

from apps.core.utils.isolated_cache_testcase import IsolatedRedisTestClient
from apps.users.models import User
from apps.users.services.user_login_service import UserLoginService


class AuthAPITestCase(IsolatedRedisTestClient):
    def setUp(self) -> None:
        super().setUp()

        # 테스트에 사용할 테스트 유저
        self.user_password: str = "TestPassword123!"
        self.user: User = User.objects.create_user(
            email="testuser@ozcoding.com",
            password=self.user_password,
            name="테스트지형",
            nickname="test_jh",
            phone_number="010-1234-5678",
        )

        # 테스트에 사용할 API URL.
        self.login_url: str = reverse("users:login")
        self.logout_url: str = reverse("users:logout")
        self.refresh_url: str = reverse("users:token_refresh")

    def test_login_success(self) -> None:
        """이메일/비밀번호로 로그인 시 토큰이 정상 발급되는지 테스트."""
        data: dict[str, str] = {"email": "testuser@ozcoding.com", "password": self.user_password}

        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 응답 바디에 access_token이 있는지 확인
        self.assertIn("access_token", response.data)
        # 쿠키에 refresh_token이 있는지 확인
        self.assertIn("refresh_token", response.cookies)

    def test_logout_success(self) -> None:
        """로그아웃 시 토큰이 Redis 블랙리스트에 등록되는지 테스트"""
        # 토큰의 유효성만 확인하 access_token 받지만 사용 x
        _, refresh_token = UserLoginService.generate_token_pair(self.user)

        # 클라이언트 쿠키에 해당 토큰을 세팅
        self.client.cookies["refresh_token"] = refresh_token

        # 로그아웃 요청
        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #  토큰이 블랙리스트에 올랐는지 검증
        self.assertTrue(UserLoginService.is_blacklisted(refresh_token))
        # 5. 쿠키가 삭제되었는지 확인
        self.assertEqual(response.cookies["refresh_token"].value, "")

    def test_token_refresh_success(self) -> None:
        """유효한 리프레시 토큰으로 재발급을 요청할 때 성공하는지 테스트합니다."""
        _, refresh_token = UserLoginService.generate_token_pair(self.user)

        # 요청 바디에 refresh token 담아서 넘김
        data: dict[str, str] = {"refresh_token": refresh_token}
        response = self.client.post(self.refresh_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 응답 확인 access token 확인
        self.assertIn("access_token", response.data)
        # 기존 토큰은 재사용을 막기 위해 블랙리스트 등록
        self.assertTrue(UserLoginService.is_blacklisted(refresh_token))

    def test_blacklisted_token_rejected(self) -> None:
        """이미 블랙리스트에 등록된 토큰으로 재발급 시도 시 403 에러가 발생하는지 테스트합니다."""
        _, refresh_token = UserLoginService.generate_token_pair(self.user)

        # 토큰을 블랙리스트에 추가
        UserLoginService.add_to_blacklist(refresh_token)

        # 차단된 토큰으로 재발급을 시도
        data: dict[str, str] = {"refresh_token": refresh_token}
        response = self.client.post(self.refresh_url, data)

        # 403 상태 코드 반환 확인
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"]["detail"], "로그인 세션이 만료되었습니다.")

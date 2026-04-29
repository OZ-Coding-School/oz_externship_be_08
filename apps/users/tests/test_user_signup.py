from django.urls import reverse
from rest_framework import status

from apps.core.utils.isolated_cache_testcase import IsolatedRedisTestClient


class SignupViewTest(IsolatedRedisTestClient):
    def setUp(self) -> None:
        super().setUp()

        self.url = reverse("users:signup")

        self.valid_payload = {
            "password": "Password1234@",
            "nickname": "테스터",
            "name": "테스터",
            "birthday": "2000-11-11",
            "gender": "M",
            "email_token": "saddfj2h4u81478ssxzcv",
            "sms_token": "24yuicdfhduf128924hv",
        }

    def test_signup_success(self)->None:
        """정상적인 데이터로 회원가입 성공 (201) 테스트"""
        response = self.client.post(self.url, data=self.valid_payload, format="json")

        # 상태 코드 201과 응답 메시지 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], "회원가입이 완료되었습니다.")

    def test_signup_missing_fields(self)->None:
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

    def test_signup_conflict(self)->None:
        """중복 가입 시도 시 409 Conflict 반환 테스트"""
        # 정상적으로 회원가입을 1회 진행하여 DB에 유저를 생성
        self.client.post(self.url, data=self.valid_payload, format="json")

        # 완전히 동일한 데이터로 다시 한번 가입을 시도
        # Serializer의 유니크 제약조건 등에 의해 ValidationError가 발생
        response = self.client.post(self.url, data=self.valid_payload, format="json")

        # 상태 코드 409 반환을 검증
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("error_detail", response.data)

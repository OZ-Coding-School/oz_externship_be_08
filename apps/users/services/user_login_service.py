import time
from typing import Tuple

from django.contrib.auth import authenticate
from django.contrib.auth.models import AbstractBaseUser
from django.core.cache import cache
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken


class UserLoginService:
    @staticmethod
    def verify_user(email: str, password: str) -> AbstractBaseUser:
        """이메일과 비밀번호를 검증하고 유저 객체를 반환."""
        user = authenticate(email=email, password=password)
        if not user:
            raise PermissionDenied("이메일 또는 비밀번호가 올바르지 않습니다.")
        # 1:1 관계 데이터를 조회
        if hasattr(user, "withdrawal") and user.withdrawal is not None:
            # PermissionDenied는 자동으로 403 Forbidden 상태 코드를 반환
            raise PermissionDenied("이미 탈퇴 처리된 회원입니다.")

        if not getattr(user, "is_active", False):
            raise PermissionDenied("비활성화된 계정입니다.")
        return user

    @staticmethod
    def generate_token_pair(user: AbstractBaseUser) -> Tuple[str, str]:
        """유저 Access Token과 Refresh Token을 생성"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token), str(refresh)

    @staticmethod
    def add_to_blacklist(refresh_token_str: str) -> None:
        """Redis 캐시에 토큰을 블랙리스트에 등록"""
        try:
            token = RefreshToken(refresh_token_str)  # type: ignore[arg-type]
            jti = token.payload.get("jti")
            exp = token.payload.get("exp")
            now = int(time.time())
            if not isinstance(exp, int) or not isinstance(jti, str):
                return
            timeout = exp - now
            if timeout > 0:
                cache.set(f"blacklist_{jti}", "true", timeout)
        except TokenError:
            pass

    @staticmethod
    def is_blacklisted(refresh_token_str: str) -> bool:
        """토큰이 블랙리스트에 존재하는지 캐시를 확인"""
        try:
            token = RefreshToken(refresh_token_str)  # type: ignore[arg-type]
            jti = token.payload.get("jti")
            return cache.get(f"blacklist_{jti}") is not None
        except TokenError:
            return True

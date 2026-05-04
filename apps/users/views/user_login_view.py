from typing import Any

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from apps.users.serializers.user_login_serializer import (
    LoginSerializer,
    TokenRefreshSerializer,
)
from apps.users.services.user_login_service import UserLoginService


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Account(로그인)"],
        summary="이메일 로그인 API",
        description="이메일과 비밀번호로 로그인합니다. Access 토큰은 바디로, Refresh 토큰은 쿠키로 반환됩니다.",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description="로그인 성공"),
            400: OpenApiResponse(description="유효성 검사 실패"),
            403: OpenApiResponse(description="비활성화 계정"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 데이터 검증 요청
        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")
        user = UserLoginService.verify_user(email, password)

        # 토큰 생성 요청
        access_token, refresh_token = UserLoginService.generate_token_pair(user)

        # HTTP 응답 및 쿠키 설정
        response = Response({"access_token": access_token}, status=status.HTTP_200_OK)

        response.set_cookie(
            key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="Lax", path="/"
        )
        return response


class LogoutView(APIView):
    permission_classes: list[Any] = []

    @extend_schema(
        tags=["Account(로그인)"],
        summary="로그아웃 API",
        request=None,
        responses={200: OpenApiResponse(description="로그아웃 성공")},
    )
    def post(self, request: Request) -> Response:
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            # 블랙리스트 등록
            UserLoginService.add_to_blacklist(refresh_token)

        response = Response({"detail": "성공적으로 로그아웃 되었습니다."}, status=status.HTTP_200_OK)
        response.delete_cookie("refresh_token")
        return response


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Account(로그인)"],
        summary="JWT 토큰 재발급 API",
        request=TokenRefreshSerializer,
        responses={
            200: OpenApiResponse(description="토큰 재발급 성공"),
            400: OpenApiResponse(description="refresh 쿠키 없음"),
            403: OpenApiResponse(description="유효하지 않은 토큰"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = TokenRefreshSerializer(data=request.data)

        #  refresh_token이 없으면 400 에러를 반환.
        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # 검증을 통과한 토큰.
        valid_refresh_token = serializer.validated_data.get("refresh_token")

        # 블랙리스트 여부 확인 요청
        if UserLoginService.is_blacklisted(valid_refresh_token):
            return Response(
                {"error_detail": {"detail": "로그인 세션이 만료되었습니다."}}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            # 토큰 재발급
            old_refresh = RefreshToken(valid_refresh_token)
            user_id = old_refresh.payload.get("user_id")
            user = User.objects.get(id=user_id)

            new_access, new_refresh = UserLoginService.generate_token_pair(user)

            UserLoginService.add_to_blacklist(valid_refresh_token)  # 기존 토큰 폐기

            # 200 성공 응답 (access_token 반환)
            response = Response({"access_token": new_access}, status=status.HTTP_200_OK)

            # 쿠키 갱신
            response.set_cookie(
                key="refresh_token", value=new_refresh, httponly=True, secure=True, samesite="Lax", path="/"
            )
            return response

        except TokenError:
            #  토큰이 만료, 변조시 403 에러를 반환
            return Response(
                {"error_detail": {"detail": "로그인 세션이 만료되었습니다."}}, status=status.HTTP_403_FORBIDDEN
            )

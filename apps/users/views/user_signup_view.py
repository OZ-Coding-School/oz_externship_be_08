from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.user_signup_serializer import SignupSerializer
from apps.users.services.user_signup_service import create_user


class SignupView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="회원가입",
        description="새로운 유저를 생성합니다. 이메일 중복 시 409 에러를 반환합니다.",
        request=SignupSerializer,
        responses={
            201: OpenApiExample(
                "성공 응답",
                value={"detail": "회원가입이 완료되었습니다."},
                response_only=True,
            ),
            400: OpenApiExample(
                "유효성 검사 실패",
                value={"error_detail": {"email": ["이 필드는 필수 항목입니다."], "password": ["너무 짧습니다."]}},
                response_only=True,
            ),
            409: OpenApiExample(
                "중복 데이터 충돌",
                value={"error_detail": "이미 가입된 이메일입니다."},
                response_only=True,
            ),
        },
        tags=["Users"],
    )
    def post(self, request: Request) -> Response:
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        create_user(serializer.validated_data)

        return Response(
            {"detail": "회원가입이 완료되었습니다."},
            status=status.HTTP_201_CREATED,
        )

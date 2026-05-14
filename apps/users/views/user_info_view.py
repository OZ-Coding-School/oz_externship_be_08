from typing import Never, cast

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.serializers.user_info_serializer import (
    UserInfoSerializer,
    UserInfoUpdateResponseSerializer,
    UserInfoUpdateSerializer,
)


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> Never:
        raise NotAuthenticated("자격 인증 데이터가 제공되지 않았습니다.")

    @extend_schema(
        tags=["accounts"],
        summary="내 정보 조회 API",
        description="로그인한 유저는 회원정보 조회가능, 수강생 등록이 되어있을 경우 수강중 과정, 기수도 조회가능",
        responses={
            200: UserInfoSerializer,
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
        },
    )
    def get(self, request: Request) -> Response:
        serializer = UserInfoSerializer(cast(User, request.user))
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["accounts"],
        summary="내 정보 수정 API",
        description="로그인한 유저는 닉네임, 이름, 생년월일, 성별 수정 가능",
        request=UserInfoUpdateSerializer,
        responses={
            200: UserInfoUpdateResponseSerializer,
            400: OpenApiResponse(description="잘못된 요청"),
            401: OpenApiResponse(description="인증 실패"),
            409: OpenApiResponse(description="중복된 닉네임"),
        },
    )
    def patch(self, request: Request) -> Response:
        user = cast(User, request.user)
        serializer = UserInfoUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_serializer = UserInfoUpdateResponseSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

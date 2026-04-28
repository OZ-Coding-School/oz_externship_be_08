from typing import NoReturn, cast

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.posts.exceptions import (
    PostAlreadyLikedError,
    PostLikeNotRegisteredError,
    PostLikePostNotFoundError,
)
from apps.posts.serializers.like import (
    PostLikeCancelResponseSerializer,
    PostLikeCreateResponseSerializer,
    PostLikeErrorResponseSerializer,
)
from apps.posts.services.like import cancel_post_like, create_post_like
from apps.users.models import User


class PostLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def permission_denied(
        self,
        request: Request,
        message: str | None = None,
        code: str | None = None,
    ) -> NoReturn:
        raise NotAuthenticated("자격 인증 데이터가 제공되지 않았습니다.")

    @extend_schema(
        tags=["posts"],
        summary="게시글 좋아요 생성",
        description="게시글 좋아요를 생성하거나 취소된 좋아요를 다시 활성화",
        responses={
            201: PostLikeCreateResponseSerializer,
            401: PostLikeErrorResponseSerializer,
            404: PostLikeErrorResponseSerializer,
            409: PostLikeErrorResponseSerializer,
        },
    )
    def post(self, request: Request, post_id: int) -> Response:
        try:
            create_post_like(
                user=cast(User, request.user),
                post_id=post_id,
            )
        except PostLikePostNotFoundError as e:
            return Response(
                {"error_detail": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except PostAlreadyLikedError as e:
            return Response(
                {"error_detail": str(e)},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(
            {"detail": "좋아요가 등록되었습니다."},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        tags=["posts"],
        summary="게시글 좋아요 취소",
        description="게시글 좋아요를 취소합니다. 단, row를 삭제하지 않고 is_liked 필드를 False로 변경합니다.",
        responses={
            200: PostLikeCancelResponseSerializer,
            401: PostLikeErrorResponseSerializer,
            404: PostLikeErrorResponseSerializer,
        },
    )
    def delete(self, request: Request, post_id: int) -> Response:
        try:
            cancel_post_like(
                user=cast(User, request.user),
                post_id=post_id,
            )
        except (PostLikePostNotFoundError, PostLikeNotRegisteredError) as e:
            return Response(
                {"error_detail": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"detail": "좋아요가 취소되었습니다."},
            status=status.HTTP_200_OK,
        )

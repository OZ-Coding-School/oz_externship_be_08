from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsRoleAdminUser
from apps.exams.serializers.exam_presigned_url_serializer import (
    ExamErrorResponseSerializer,
    ExamPresignedUrlRequestSerializer,
    ExamPresignedUrlResponseSerializer,
)
from apps.exams.services.exam_presigned_url_service import presigned_url_generation


# TODO: 권한 에러메시지 detail에서 error_detail로 수정하는 믹스인 추가
class PresignedUrlView(APIView):
    permission_classes = [IsRoleAdminUser]

    @extend_schema(
        tags=["exams"],
        summary="exams presigned_url",
        request=ExamPresignedUrlRequestSerializer,
        responses={
            200: ExamPresignedUrlResponseSerializer,
            400: OpenApiResponse(
                description="error_detail: 파일을 첨부해주세요, 지원하지 않는 파일 형식입니다.",
                response=ExamErrorResponseSerializer,
            ),
            401: ExamErrorResponseSerializer,
            403: ExamErrorResponseSerializer,
        },
    )
    def put(self, request: Request) -> Response:
        try:
            presigned_url, img_url, key = presigned_url_generation(request.data.get("file_name", ""))
        except ValueError as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"presigned_url": presigned_url, "img_url": img_url, "key": key}, status=status.HTTP_200_OK)

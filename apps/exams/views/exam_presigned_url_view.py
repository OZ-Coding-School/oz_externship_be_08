from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsRoleAdminUser
from apps.core.utils.s3_urls import s3


# TODO: 권한 에러메시지 detail에서 error_detail로 수정하는 믹스인 추가
class PresignedUrlView(APIView):
    permission_classes = [IsRoleAdminUser]
    PATH = "uploads/exams/thumbnails"

    def put(self, request: Request) -> Response:
        try:
            file_name = request.data.get("file_name")
            path = self.PATH
            presigned_url, img_url, key = s3.create_upload_urls(file_name, path)
        except ValueError as e:
            return Response({"error_detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"presigned_url": presigned_url, "img_url": img_url, "key": key}, status=status.HTTP_200_OK)

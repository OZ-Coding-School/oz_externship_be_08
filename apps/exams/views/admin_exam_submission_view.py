from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsRoleAdminUser
from apps.exams.serializers.admin_exam_submission_serializer import (
    AdminExamSubmissionListQuerySerializer,
    AdminExamSubmissionListSerializer,
)
from apps.exams.services.admin_exam_submission_service import get_submission_list


class AdminExamSubmissionView(APIView):
    permission_classes = [IsRoleAdminUser]

    def permission_denied(self, request, message=None, code=None):
        if request.authenticators and not request.successful_authenticator:
            raise NotAuthenticated("자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied("쪽지시험 응시 내역 조회 권한이 없습니다.")

    def get(self, request):
        query_serializer = AdminExamSubmissionListQuerySerializer(data=request.query_params)
        if not query_serializer.is_valid():
            return Response({"error_detail": "유효하지 않은 조회 요청입니다."}, status=status.HTTP_400_BAD_REQUEST)

        submissions = get_submission_list(query_serializer.validated_data)

        if not submissions.exists():
            return Response({"error_detail": "조회된 응시 내역이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        paginator = PageNumberPagination()
        paginated = paginator.paginate_queryset(submissions, request)

        serializer = AdminExamSubmissionListSerializer(paginated, many=True)
        return paginator.get_paginated_response(serializer.data)
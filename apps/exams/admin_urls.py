from django.urls import path
from drf_spectacular.utils import extend_schema

from apps.core.presigned_url.views import PresignedUrlView
from apps.core.utils.permissions import IsRoleAdminUser
from apps.exams.views.admin_exam_deployment_view import (
    AdminExamDeploymentDetailView,
    AdminExamDeploymentStatusView,
    AdminExamDeploymentView,
)
from apps.exams.views.admin_exam_question_view import (
    AdminQuestionCreateView,
    AdminQuestionUpdateDeleteView,
)
from apps.exams.views.admin_exam_submission_view import (
    AdminExamSubmissionDetailView,
    AdminExamSubmissionView,
)
from apps.exams.views.admin_exam_view import ExamDetailView, ExamListCreateView


@extend_schema(tags=["admin-exams"])
class ExamImageUploadView(PresignedUrlView):
    path = "uploads/exams/thumbnails"
    permission_classes = [IsRoleAdminUser]


urlpatterns = [
    path("submissions/", AdminExamSubmissionView.as_view(), name="exam-submission-list"),
    path("submissions/<int:submission_id>/", AdminExamSubmissionDetailView.as_view(), name="exam-submission-detail"),
    path("deployments", AdminExamDeploymentView.as_view(), name="exam-deployment"),
    path("deployments/<str:deployment_id>", AdminExamDeploymentDetailView.as_view(), name="exam-deployment-detail"),
    path(
        "deployments/<str:deployment_id>/status",
        AdminExamDeploymentStatusView.as_view(),
        name="exam-deployment-status",
    ),
    path("presigned-url", ExamImageUploadView.as_view(), name="presigned-url"),
    path("<int:exam_id>/questions", AdminQuestionCreateView.as_view(), name="exam-question-create"),
    path("questions/<int:question_id>", AdminQuestionUpdateDeleteView.as_view(), name="exam-question-update-delete"),
    path("<int:exam_id>", ExamDetailView.as_view(), name="exam-detail"),
    path("", ExamListCreateView.as_view(), name="exam-list"),
]

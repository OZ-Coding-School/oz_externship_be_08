from django.urls import path

from apps.exams.views.exam_deployment_view import (
    ExamDeploymentCheckCodeView,
    ExamDeploymentDetailView,
    ExamDeploymentListView,
    ExamDeploymentStatusView,
)
from apps.exams.views.user_exam_submission_view import UserExamSubmissionCreateView, UserExamSubmissionGetView

urlpatterns = [
    path("submissions/", UserExamSubmissionCreateView.as_view(), name="user-exam-submission-create"),
    path("submissions/<int:submission_id>", UserExamSubmissionGetView.as_view(), name="user-exam-submission-get"),
    path("deployments/", ExamDeploymentListView.as_view(), name="deployment"),
    path("deployments/<int:deployment_id>/check-code/", ExamDeploymentCheckCodeView.as_view(), name="deployment-code"),
    path("deployments/<int:deployment_id>/", ExamDeploymentDetailView.as_view(), name="deployment-detail"),
    path("deployments/<int:deployment_id>/status/", ExamDeploymentStatusView.as_view(), name="deployment-status"),
]

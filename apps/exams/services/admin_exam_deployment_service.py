import json
import uuid
from typing import Any

from django.core.serializers.json import DjangoJSONEncoder
from django.db import DatabaseError, transaction
from django.db.models import Avg, Count, QuerySet

from apps.core.utils.base62 import Base62
from apps.exams.exceptions.admin_exam_deployment_exception import (
    DeploymentConflictError,
    DeploymentDeleteConflictError,
    DeploymentDeleteNotFoundError,
    DeploymentDetailNotFoundError,
    DeploymentNoQuestionsError,
    DeploymentNotFoundError,
    DeploymentStatusConflictError,
    DeploymentStatusNotFoundError,
    DeploymentUpdateNotFoundError,
)
from apps.exams.models.exam_deployment_model import ExamDeployment
from apps.exams.models.exam_model import Exam
from apps.exams.models.exam_submission_model import ExamSubmission
from apps.posts.models import Cohort
from apps.users.models import CohortStudents

SORT_FIELD_MAP = {
    "created_at": "created_at",
    "submit_count": "submit_count",
    "avg_score": "avg_score",
}


def create_access_code(length: int = 8) -> str:
    while True:
        code = Base62.uuid_encode(uuid.uuid4(), length=length)
        if not ExamDeployment.objects.filter(access_code=code).exists():
            return code


@transaction.atomic
def create_deployment(validated_data: dict[str, Any]) -> ExamDeployment:
    exam_id = validated_data["exam_id"]
    cohort_id = validated_data["cohort_id"]

    deployment_data = validated_data.copy()
    deployment_data.pop("exam_id")
    deployment_data.pop("cohort_id")

    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        raise DeploymentNotFoundError()

    try:
        cohort = Cohort.objects.get(id=cohort_id)
    except Cohort.DoesNotExist:
        raise DeploymentNotFoundError()

    if ExamDeployment.objects.filter(exam=exam, cohort=cohort).exists():
        raise DeploymentConflictError()

    snapshot = json.loads(json.dumps(list(exam.examquestion_set.values()), cls=DjangoJSONEncoder))
    if not snapshot:
        raise DeploymentNoQuestionsError()

    for q in snapshot:
        answer = q.get("answer", [])
        if isinstance(answer, str):
            q["answer"] = [answer]

    access_code = create_access_code()

    deployment = ExamDeployment.objects.create(
        **deployment_data,
        exam=exam,
        cohort=cohort,
        questions_snapshot_json=snapshot,
        access_code=access_code,
    )

    return deployment


def get_deployment_list(validated_params: dict[str, Any]) -> QuerySet[ExamDeployment]:
    subject_id = validated_params.get("subject_id")
    cohort_id = validated_params.get("cohort_id")
    search_keyword = validated_params.get("search_keyword")
    sort = validated_params.get("sort", "created_at")
    order = validated_params.get("order", "desc")

    qs = ExamDeployment.objects.select_related("exam__subject", "cohort__course")

    if subject_id:
        qs = qs.filter(exam__subject_id=subject_id)
    if cohort_id:
        qs = qs.filter(cohort_id=cohort_id)
    if search_keyword:
        qs = qs.filter(exam__title__icontains=search_keyword)

    # TODO : ExamSubmission.deployment ForeignKey에 related_name 추가 시 "examsubmission" → 해당 이름으로 변경
    qs = qs.annotate(
        submit_count=Count("examsubmission"),
        avg_score=Avg("examsubmission__score"),
    )

    sort_field = SORT_FIELD_MAP.get(sort, "created_at")

    qs = qs.order_by(f"-{sort_field}" if order == "desc" else sort_field)

    return qs


def get_deployment_target_student_count(cohort_id: int) -> int:
    return CohortStudents.objects.filter(cohort_id=cohort_id).count()


def get_deployment_submitted_student_count(deployment_id: int) -> int:
    return ExamSubmission.objects.filter(deployment_id=deployment_id).count()


def calculate_not_submitted_count(
    total_student_count: int,
    submit_count: int,
) -> int:
    return max(total_student_count - submit_count, 0)


def get_deployment_detail(deployment_id: int) -> ExamDeployment:
    try:
        deployment = ExamDeployment.objects.select_related(
            "exam__subject",
            "cohort__course",
        ).get(id=deployment_id)
    except ExamDeployment.DoesNotExist:
        raise DeploymentDetailNotFoundError()

    total_student_count = get_deployment_target_student_count(
        cohort_id=deployment.cohort_id,
    )

    submit_count = get_deployment_submitted_student_count(
        deployment_id=deployment.id,
    )

    setattr(deployment, "submit_count", submit_count)
    setattr(
        deployment,
        "not_submitted_count",
        calculate_not_submitted_count(
            total_student_count=total_student_count,
            submit_count=submit_count,
        ),
    )

    return deployment


@transaction.atomic
def update_deployment(deployment_id: int, validated_data: dict[str, Any]) -> ExamDeployment:
    try:
        deployment = ExamDeployment.objects.select_for_update(nowait=True).get(id=deployment_id)
    except ExamDeployment.DoesNotExist:
        raise DeploymentUpdateNotFoundError()
    except DatabaseError:
        raise DeploymentConflictError()

    for field, value in validated_data.items():
        setattr(deployment, field, value)
    deployment.save(update_fields=list(validated_data.keys()))

    return deployment


@transaction.atomic
def delete_deployment(deployment_id: int) -> ExamDeployment:
    try:
        deployment = ExamDeployment.objects.select_for_update(nowait=True).get(id=deployment_id)
    except ExamDeployment.DoesNotExist:
        raise DeploymentDeleteNotFoundError()
    except Exception:
        raise DeploymentDeleteConflictError()

    deployment.delete()
    return deployment


@transaction.atomic
def update_deployment_status(deployment_id: int, status: str) -> ExamDeployment:
    try:
        deployment = ExamDeployment.objects.select_for_update(nowait=True).get(id=deployment_id)
    except ExamDeployment.DoesNotExist:
        raise DeploymentStatusNotFoundError()
    except DatabaseError:
        raise DeploymentStatusConflictError()

    deployment.status = status
    deployment.save(update_fields=["status"])
    return deployment

from typing import Any

from django.db.models import Q, QuerySet

from apps.exams.models.exam_submission_model import ExamSubmission

SORT_FIELD_MAP = {
    "created_at": "created_at",
    "score": "score",
}


def get_submission_list(validated_params: dict[str, Any]) -> QuerySet[ExamSubmission]:
    cohort_id = validated_params.get("cohort_id")
    exam_id = validated_params.get("exam_id")
    search_keyword = validated_params.get("search_keyword")
    sort = validated_params.get("sort", "created_at")
    order = validated_params.get("order", "desc")

    qs = ExamSubmission.objects.select_related(
        "submitter",
        "deployment__cohort__course",
        "deployment__exam__subject",
    )

    if cohort_id:
        qs = qs.filter(deployment__cohort_id=cohort_id)
    if exam_id:
        qs = qs.filter(deployment__exam_id=exam_id)
    if search_keyword:
        qs = qs.filter(Q(submitter__name__icontains=search_keyword) | Q(submitter__nickname__icontains=search_keyword))

    sort_field = SORT_FIELD_MAP.get(sort, "created_at")
    qs = qs.order_by(f"-{sort_field}" if order == "desc" else sort_field)

    return qs

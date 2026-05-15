from typing import Any

from apps.exams.exceptions.exam_submission_exception import (
    DeploymentNotFound,
    SubmissionAlreadyExists,
    UserSubmissionNotFound,
)
from apps.exams.models import ExamDeployment, ExamSubmission


def get_submission_detail(submitter: int, submission_id: int) -> ExamSubmission:
    try:
        return ExamSubmission.objects.select_related("deployment__exam").get(
            submitter=submitter, id=submission_id
        )
    except ExamSubmission.DoesNotExist:
        raise UserSubmissionNotFound()


def create_submission(submitter_id: int, validated_data: dict[str, Any]) -> ExamSubmission:
    deployment_id = validated_data["deployment_id"]
    started_at = validated_data["started_at"]
    cheating_count = validated_data["cheating_count"]
    answers = validated_data["answers"]

    try:
        deployment = ExamDeployment.objects.get(id=deployment_id)
    except ExamDeployment.DoesNotExist:
        raise DeploymentNotFound()

    if ExamSubmission.objects.filter(submitter_id=submitter_id, deployment=deployment).exists():
        raise SubmissionAlreadyExists()

    snapshot_map = {str(q["id"]): q for q in deployment.questions_snapshot_json}
    answer_json: dict[str, list[str]] = {}
    score = 0
    correct_count = 0

    for answer in answers:
        q_id = str(answer["question_id"])
        submitted = answer["submitted_answer"]
        submitted_list = [submitted] if isinstance(submitted, str) else list(submitted)
        answer_json[q_id] = submitted_list

        snap_q = snapshot_map.get(q_id)
        if snap_q and submitted_list == snap_q.get("answer", []):
            score += snap_q.get("point", 0)
            correct_count += 1

    return ExamSubmission.objects.create(
        submitter_id=submitter_id,
        deployment=deployment,
        started_at=started_at,
        cheating_count=cheating_count,
        answer_json=answer_json,
        score=score,
        correct_answer_count=correct_count,
    )

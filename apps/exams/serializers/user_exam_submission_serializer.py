import json
from typing import Any

from rest_framework import serializers

from apps.exams.models import Exam, ExamSubmission


class ExamNestedSerializer(serializers.ModelSerializer[Exam]):
    class Meta:
        model = Exam
        fields = ["id", "title", "thumbnail_img_url"]
        read_only_fields = ["id", "title", "thumbnail_img_url"]


class UserExamSubmissionGetSerializer(serializers.ModelSerializer[ExamSubmission]):
    exam = ExamNestedSerializer(source="deployment.exam")
    questions = serializers.SerializerMethodField()
    total_score = serializers.SerializerMethodField()
    submitted_at = serializers.DateTimeField(source="created_at")
    elapsed_time = serializers.SerializerMethodField()

    def get_questions(self, obj: ExamSubmission) -> list[dict[str, Any]]:
        answer_json: dict[str, list[str]] = obj.answer_json
        result = []
        for q in obj.deployment.questions_snapshot_json:
            q_id = str(q["id"])
            submitted = answer_json.get(q_id, [])
            options_json = q.get("options_json")
            result.append(
                {
                    "id": q["id"],
                    "question": q["question"],
                    "prompt": q.get("prompt"),
                    "blank_count": q.get("blank_count"),
                    "options": json.loads(options_json) if options_json else None,
                    "type": q.get("type"),
                    "answer": q.get("answer"),
                    "point": q["point"],
                    "explanation": q.get("explanation", ""),
                    "is_correct": submitted == q.get("answer", []),
                    "submitted_answer": submitted,
                }
            )
        return result

    def get_total_score(self, obj: ExamSubmission) -> int:
        questions = obj.deployment.questions_snapshot_json
        return sum(q.get("point", 0) for q in questions)

    def get_elapsed_time(self, obj: ExamSubmission) -> int:
        return int((obj.created_at - obj.started_at).total_seconds())

    class Meta:
        model = ExamSubmission
        fields = [
            "id",
            "submitter_id",
            "deployment_id",
            "exam",
            "questions",
            "cheating_count",
            "score",
            "total_score",
            "correct_answer_count",
            "elapsed_time",
            "started_at",
            "submitted_at",
        ]


class QuestionsSchemaSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    question = serializers.CharField()
    prompt = serializers.CharField()
    blank_count = serializers.IntegerField()
    options = serializers.ListField(child=serializers.CharField())
    type = serializers.CharField()
    answer = serializers.ListField(child=serializers.CharField())
    point = serializers.IntegerField()
    explanation = serializers.CharField()
    is_correct = serializers.BooleanField()
    submitted_answer = serializers.ListField(child=serializers.CharField())


class UserExamSubmissionExtendSchemaSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    submitter_id = serializers.IntegerField()
    deployment_id = serializers.IntegerField()
    exam = ExamNestedSerializer()
    questions = QuestionsSchemaSerializer(many=True)
    cheating_count = serializers.IntegerField()
    score = serializers.IntegerField()
    total_score = serializers.IntegerField()
    correct_answer_count = serializers.IntegerField()
    elapsed_time = serializers.IntegerField()
    started_at = serializers.DateTimeField()
    submitted_at = serializers.DateTimeField()


class AnswerItemSerializer(serializers.Serializer[Any]):
    question_id = serializers.IntegerField(min_value=1)
    type = serializers.ChoiceField(
        choices=["single_choice", "multiple_choice", "short_answer", "fill_blank", "ox", "ordering"]
    )
    submitted_answer = serializers.JSONField(required=False, default=list)  # type: ignore[arg-type]


class UserExamSubmissionCreateSerializer(serializers.Serializer[Any]):
    deployment_id = serializers.IntegerField(min_value=1)
    started_at = serializers.DateTimeField()
    cheating_count = serializers.IntegerField(min_value=0, max_value=3)
    answers = AnswerItemSerializer(many=True)


class UserExamSubmissionCreateResponseSerializer(serializers.Serializer[Any]):
    submission_id = serializers.IntegerField()
    score = serializers.IntegerField()
    correct_answer_count = serializers.IntegerField()
    redirect_url = serializers.CharField()

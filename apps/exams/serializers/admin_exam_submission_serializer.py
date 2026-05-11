from typing import Any

from rest_framework import serializers


class AdminExamSubmissionListQuerySerializer(serializers.Serializer[Any]):
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    page_size = serializers.IntegerField(required=False, min_value=1)
    search_keyword = serializers.CharField(required=False, allow_blank=True)
    cohort_id = serializers.IntegerField(required=False, min_value=1)
    exam_id = serializers.IntegerField(required=False, min_value=1)
    sort = serializers.ChoiceField(choices=["created_at", "score"], default="created_at", required=False)
    order = serializers.ChoiceField(choices=["asc", "desc"], default="desc", required=False)


class AdminExamSubmissionListSerializer(serializers.Serializer[Any]):
    submission_id = serializers.IntegerField(source="id")
    nickname = serializers.CharField(source="submitter.nickname")
    name = serializers.CharField(source="submitter.name")
    course_name = serializers.CharField(source="deployment.cohort.course.name")
    cohort_number = serializers.IntegerField(source="deployment.cohort.number")
    exam_title = serializers.CharField(source="deployment.exam.title")
    subject_name = serializers.CharField(source="deployment.exam.subject.title")
    score = serializers.IntegerField()
    cheating_count = serializers.IntegerField()
    started_at = serializers.DateTimeField()
    finished_at = serializers.DateTimeField(source="created_at")


class AdminExamSubmissionPathSerializer(serializers.Serializer[Any]):
    submission_id = serializers.IntegerField(min_value=1)


class ExamDetailSerializer(serializers.Serializer[Any]):
    exam_title = serializers.CharField(source="exam.title")
    subject_name = serializers.CharField(source="exam.subject.title")
    duration_time = serializers.IntegerField()
    open_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    close_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")


class StudentDetailSerializer(serializers.Serializer[Any]):
    nickname = serializers.CharField(source="submitter.nickname")
    name = serializers.CharField(source="submitter.name")
    course_name = serializers.CharField(source="deployment.cohort.course.name")
    cohort_number = serializers.IntegerField(source="deployment.cohort.number")


class ResultDetailSerializer(serializers.Serializer[Any]):
    score = serializers.IntegerField()
    correct_answer_count = serializers.IntegerField()
    cheating_count = serializers.IntegerField()
    total_question_count = serializers.SerializerMethodField()
    elapsed_time = serializers.SerializerMethodField()

    def get_total_question_count(self, obj: Any) -> int:
        return len(obj.deployment.questions_snapshot_json)

    def get_elapsed_time(self, obj: Any) -> int:
        return int((obj.created_at - obj.started_at).total_seconds() // 60)


class QuestionDetailSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    number = serializers.IntegerField()
    type = serializers.CharField()
    question = serializers.CharField()
    prompt = serializers.CharField(allow_null=True)
    options = serializers.ListField(
        child=serializers.CharField(),
        allow_null=True,
        allow_empty=True,
    )
    point = serializers.IntegerField()
    answer = serializers.JSONField()
    submitted_answer = serializers.JSONField(allow_null=True)
    is_correct = serializers.BooleanField()
    explanation = serializers.CharField()


class AdminExamSubmissionDetailSerializer(serializers.Serializer[Any]):
    exam = ExamDetailSerializer(source="deployment")
    student = StudentDetailSerializer(source="*")
    result = ResultDetailSerializer(source="*")
    questions = serializers.SerializerMethodField()

    def get_questions(self, obj: Any) -> list[dict[str, Any]]:
        snapshot = obj.deployment.questions_snapshot_json
        answers = obj.answer_json
        questions = []
        for idx, q in enumerate(snapshot, start=1):
            q_id = str(q.get("id"))
            answer_data = answers.get(q_id, {})
            questions.append(
                {
                    "id": q.get("id"),
                    "number": idx,
                    "type": q.get("type"),
                    "question": q.get("question"),
                    "prompt": q.get("prompt"),
                    "options": q.get("options"),
                    "point": q.get("point"),
                    "answer": q.get("answer"),
                    "submitted_answer": answer_data.get("submitted_answer"),
                    "is_correct": answer_data.get("is_correct", False),
                    "explanation": q.get("explanation"),
                }
            )
        return questions

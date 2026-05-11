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

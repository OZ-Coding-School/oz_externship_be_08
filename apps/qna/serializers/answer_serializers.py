from rest_framework import serializers

from apps.qna.models.answer_models import Answers


class AnswerRequestSerializer(serializers.Serializer[Answers]):
    content = serializers.CharField(required=True)
    img_urls = serializers.ListField(
        child=serializers.CharField(),
        required=True,
    )


class AnswerResponseSerializer(serializers.ModelSerializer[Answers]):
    answer_id = serializers.IntegerField(source="id")
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Answers
        fields = (
            "answer_id",
            "question_id",
            "author_id",
            "created_at",
        )

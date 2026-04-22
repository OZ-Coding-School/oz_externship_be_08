from typing import Any

from rest_framework import serializers

from apps.qna.models.answer_models import AnswerImages, Answers


class AnswerRequestSerializer(serializers.Serializer[Answers]):
    content = serializers.CharField(required=True)
    img_url = serializers.ListField(
        child=serializers.CharField(),
        required=True,
    )

    def create(self, validated_data: dict[str, Any]) -> Answers:
        image_data = validated_data.pop("img_url")
        answer = Answers.objects.create(**validated_data)
        for img in image_data:
            AnswerImages.objects.create(img_url=img, answer=answer)
        return answer


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

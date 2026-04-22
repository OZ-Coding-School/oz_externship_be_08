from apps.qna.models.answer_models import AnswerImages, Answers


def answer_create(content: str, img_urls: list[str], question_id: int, author_id: int) -> Answers:
    answer = Answers.objects.create(
        question_id=question_id,
        author_id=author_id,
        content=content,
    )
    for img in img_urls:
        AnswerImages.objects.create(img_url=img, answer=answer)
    return answer

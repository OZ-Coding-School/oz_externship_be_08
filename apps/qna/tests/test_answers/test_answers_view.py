from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.qna.models.question_models import QuestionCategories, Questions
from apps.users.models import User


class BaseTestCase(APITestCase):
    """다른 test class 여서도 동일하게 사용가능하게 구현"""

    def setUp(self) -> None:
        """유저 데이터 및 question test 데이터 생성"""
        self.user = User.objects.create_user(
            name="name",
            email="test@test.com",
            nickname="test",
            phone_number="01011111111",
            gender="Male",
            birthday="2000-01-01",
            is_active=True,
            role="USER",
            password="testpassword",
        )
        self.category = QuestionCategories.objects.create(name="python")
        self.question = Questions.objects.create(
            author=self.user,
            category=self.category,
            title="testquestion",
            content="testcontent",
            view_count=0,
        )


class AnswersViewTestCase(BaseTestCase):
    """
    답변 등록 API
    /api/v1/qna/questions/{question_id}/answers
    post 테스트
    """

    def setUp(self) -> None:
        self.client = APIClient()
        super().setUp()

    def test_answer_create(self) -> None:
        self.answer = {
            "content": "testcontent",
            "img_urls": ["testimageurl"],
        }
        self.client.force_authenticate(user=self.user)
        url = reverse("question_answers", kwargs={"question_id": self.question.id})
        response = self.client.post(url, self.answer, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["question_id"], self.question.id)
        self.assertEqual(response.data["author_id"], self.user.id)
        self.assertIn("created_at", response.data)
        self.assertIn("answer_id", response.data)

    def test_answer_create_invalid(self) -> None:
        self.answer = {
            "content": "testcontent",
        }
        self.client.force_authenticate(user=self.user)
        url = reverse("question_answers", kwargs={"question_id": self.question.id})
        response = self.client.post(url, self.answer, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

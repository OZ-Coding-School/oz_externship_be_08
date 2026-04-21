from django.test import TestCase
from apps.qna.models.answer_models import Answers,AnswerImages,AnswerComments
from apps.qna.models.question_models import Questions,QuestionCategories
from django.contrib.auth import get_user_model

User = get_user_model()

class BaseTestCase(TestCase):
    """다른 test class 여서도 동일하게 사용가능하게 구현 """
    def setUp(self)->None:
        """유저 데이터 및 question test 데이터 생성"""
        self.user = User.objects.create_user(
            name="name",
            email="test@test.com",
            nickname = "test",
            phone_number = "01011111111",
            gender = "Male",
            birthday = "2000-01-01",
            is_active = True,
            role = "USER",
            password = "testpassword",

        )
        self.category = QuestionCategories.objects.create(name="python")
        self.question = Questions.objects.create(
            author = self.user,
            category = self.category,
            title = "testquestion",
            content = "testcontent",
            view_count = 0,
        )


class AnswersTest(BaseTestCase):
    def setUp(self)->None:
        super().setUp()

    def test_create_answer(self)->None:
        """Answers 모델 생성 test"""
        self.answer = Answers.objects.create(
            author=self.user,
            question=self.question,
            content="testcontent",
            is_adopted=False,
        )

        self.assertEqual(Answers.objects.count(), 1)
        self.assertEqual(self.answer.author,self.user)
        self.assertEqual(self.answer.question,self.question)
        self.assertEqual(self.answer.content,"testcontent")
        self.assertEqual(self.answer.is_adopted,False)

    def test_create_answer_without_content(self)->None:
        """Answers 모델 content 데이터 뼤고 생성시"""
        with self.assertRaises(Exception):
            answer = Answers(author=self.user, question=self.question)
            answer.full_clean()
    def test_create_answer_without_author(self)->None:
        """Answers 모델 작성자 데이터 뼤고 생성시"""
        with self.assertRaises(Exception):
            Answers.objects.create(
                question = self.question,
                content = "testcontent",
            )


    def test_create_answer_without_question(self)->None:
        """Answers 모델 질문 데이터 뼤고 생성시"""
        with self.assertRaises(Exception):
            Answers.objects.create(
                author = self.user,
                content = "testcontent",
            )

class AnswerImagesTest(BaseTestCase):
    def setUp(self)->None:
        super().setUp()
        self.answer = Answers.objects.create(
            author=self.user,
            question=self.question,
            content="testcontent",
        )
    def test_create_answer_image(self)->None:
        """AnswerImages 모델 생성 test"""
        self.answer_image = AnswerImages.objects.create(
            answer = self.answer,
            img_url="testurl",
        )

        self.assertEqual(AnswerImages.objects.count(), 1)
        self.assertEqual(self.answer.author,self.user)
        self.assertEqual(self.answer_image.img_url,"testurl")

    def test_create_answer_image_without_answer(self)->None:
        """AnswersImage 모델 답변 데이터 뼤고 생성시"""
        with self.assertRaises(Exception):
            AnswerImages.objects.create(
                img_url="testurl",
            )



    def test_create_answer_image_without_img(self)->None:
        """AnswersImage 모델 이미지 데이터 뼤고 생성시"""
        with self.assertRaises(Exception):
            self.answer_image = AnswerImages(answer = self.answer,)
            self.answer_image.full_clean()

class AnswersCommentsTest(BaseTestCase):
    """AnswersComments 모델 test"""
    def setUp(self)->None:
        super().setUp()
        self.answer = Answers.objects.create(
            author=self.user,
            question=self.question,
            content="testcontent",
        )
    def test_create_answer_comment(self)->None:
        """AnswerComment 모델 생성"""
        self.answer_comment = AnswerComments.objects.create(
            author=self.user,
            answer = self.answer,
            content = "testcontent",
        )

        self.assertEqual(AnswerComments.objects.count(), 1)
        self.assertEqual(self.answer.author,self.user)
        self.assertEqual(self.answer_comment.answer,self.answer)
        self.assertEqual(self.answer_comment.content,"testcontent")

    def test_create_answer_comment_without_answer(self)->None:
        """answer 데이터 뺴고 생성"""
        with self.assertRaises(Exception):
            AnswerComments.objects.create(
                author = self.user,
                content="testcontent",
            )
    def test_create_answer_comment_without_author(self)->None:
        """author 데이터 뺴고 생성"""
        with self.assertRaises(Exception):
            AnswerComments.objects.create(
                answer = self.answer,
                content="testcontent",
            )
    def test_create_answer_comment_without_comment(self)->None:
        """comment 데이터 뺴고 생성"""
        with self.assertRaises(Exception):
            comment = AnswerComments(author=self.user, answer=self.answer)
            comment.full_clean()
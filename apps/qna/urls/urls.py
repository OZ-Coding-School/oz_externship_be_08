from django.urls import path
from apps.qna.views import answer_views

urlpatterns = [
    path("qna/questions/<int:question_id>/answers",answer_views.AnswerView.as_view(),name = "question_answers"),
]
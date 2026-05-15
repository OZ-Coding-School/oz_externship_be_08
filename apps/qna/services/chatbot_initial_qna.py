from dataclasses import asdict
from time import sleep

from django.conf import settings

from apps.qna.chatbot import GROQ_MODEL, QNA_PROMPT, GroqPayloadFactory, call_groq_once
from apps.qna.chatbot.exceptions import GroqAPIError, GroqTimeoutError
from apps.qna.dtos import InitialQNA
from apps.qna.exceptions import (
    ConflictException,
    ExternalAPIException,
    ExternalAPITimeoutException,
    GetInitialTimeoutException,
    NotFoundException,
)
from apps.qna.models import Question, QuestionCategory
from apps.qna.redis import CacheFactory, CacheRepository
from apps.qna.redis.keys import INITIAL_KEY, LOCK_KEY


class InitialService:
    MODEL = GROQ_MODEL["gpt_120"]
    INITIAL_TTL = 60 * 60 * 24 * 7
    LOCK_TTL = 60
    GROQ_TIMEOUT = (5, 60)

    @staticmethod
    def get_initial_answer(question_id: int) -> InitialQNA:

        key = INITIAL_KEY.format(question_id=question_id)
        cached = CacheRepository.get_initial(key)
        if cached:
            return cached

        lock_key = LOCK_KEY.format(key=key)
        if not CacheRepository.acquire_lock(lock_key, InitialService.LOCK_TTL):
            timeout = 20
            interval = 2
            elapsed = 0
            while elapsed < timeout:
                sleep(interval)
                elapsed += interval
                cached = CacheRepository.get_initial(key)
                if cached:
                    return cached
            raise GetInitialTimeoutException()

        try:
            try:
                return InitialService.save_initial_answer(question_id)
            except ConflictException:
                cached = CacheRepository.get_initial(key)
                if cached:
                    return cached
                raise
        finally:
            CacheRepository.delete(lock_key)

    @staticmethod
    def save_initial_answer(question_id: int) -> InitialQNA:
        """
        초기응답 생성용 서비스 함수입니다.
        동시요청 가능성이 없어 락을 구현하지 않았습니다.
        초기응답은 모든 클라이언트에게 동일하게 제공되므로 캐시 키에 user_id를 포함하지 않습니다.
        """
        if CacheRepository.get_initial(INITIAL_KEY.format(question_id=question_id)):
            raise ConflictException("이미 AI가 답변을 생성했습니다.")

        question = Question.objects.filter(pk=question_id).select_related("category__parent__parent").first()
        if not question:
            raise NotFoundException("질문 데이터를 찾을 수 없습니다.")

        categories = InitialService._get_categories(question.category)
        save_data = CacheFactory.create_initial_cache(
            category=categories,
            title=question.title,
            content=question.content,
            answer=InitialService._create_initial_answer(question, categories),
            question_id=question.id,
            using_model=InitialService.MODEL,
        )

        key = INITIAL_KEY.format(question_id=question.id)
        CacheRepository.save_initial(key=key, value=asdict(save_data), ttl=InitialService.INITIAL_TTL)

        return save_data

    @staticmethod
    def _create_initial_answer(question: Question, categories: str) -> str:
        payload = GroqPayloadFactory.create_initial_payload(
            prompt=QNA_PROMPT,
            category=categories,
            title=question.title,
            message=question.content,
            stream=False,
            model=InitialService.MODEL,
        )

        try:
            return call_groq_once(payload.api(), key=settings.GROQ_API_KEY, timeout=InitialService.GROQ_TIMEOUT)
        except GroqTimeoutError:
            raise ExternalAPITimeoutException()
        except GroqAPIError:
            raise ExternalAPIException()

    @staticmethod
    def _get_categories(category: QuestionCategory) -> str:
        middle = category.parent
        if middle is None:
            return category.name

        top = middle.parent
        if top is None:
            return f"{middle.name} > {category.name}"

        return f"{top.name} > {middle.name} > {category.name}"

from dataclasses import asdict
from typing import Iterator

from apps.qna.chatbot import GROQ_MODEL, QNA_PROMPT, GroqPayloadFactory
from apps.qna.dtos import InitialQNA, LastQNAHistory, Message, QNAChatbotContext
from apps.qna.exceptions import (
    ConversationOverException,
    InactiveSessionException,
    NotFoundException,
)
from apps.qna.redis import CacheFactory, CacheRepository
from apps.qna.redis.keys import INITIAL_KEY, QNA_KEY, SESSION_KEY
from apps.qna.services.chatbot_base import ChatbotBaseService


class QNAChatbotService(ChatbotBaseService):
    QNA_TTL = 60 * 30
    MODEL = GROQ_MODEL["gpt_120"]

    @staticmethod
    def response_qna_history(user_id: int, question_id: int) -> list[Message]:
        """
        qna 채팅 히스토리 조회용 함수입니다.
        유저가 히스토리를 조회함으로써 세션이 처음 활성화됩니다.
        히스토리가 없는 경우 빈 문자열을 반환합니다.
        """
        initial = CacheRepository.get_initial(INITIAL_KEY.format(question_id=question_id))
        if initial is None:
            raise NotFoundException("해당 질문을 찾을 수 없습니다.")
        return QNAChatbotService._return_qna_history(user_id, question_id, initial)

    @staticmethod
    def response_qna_chat(initial: InitialQNA, history: list[Message] | None, key: str, message: str) -> Iterator[str]:
        """
        qna 채팅 대화용 함수입니다.
        세션 활성화는 히스토리 조회에서 이뤄지고, 이곳에서는 해당 세션을 검증합니다.
        유저의 질문과 챗봇의 응답 한 쌍을 하나의 대화로 취급되며,
        만약 캐시에 저장된 대화의 길이가 5쌍 이상일 경우, 사용자의 다음 채팅에 대해 429를 반환합니다.
        대화 히스토리와 세션의 ttl은 30분이며, 대화가 갱신될때마다 같이 갱신됩니다.
        """
        payload = GroqPayloadFactory.create_payload(
            prompt=QNA_PROMPT,
            message=message,
            history=GroqPayloadFactory.build_history_for_qna_payload(initial, history),
            model=QNAChatbotService.MODEL,
        )
        return QNAChatbotService._stream_and_save_chat(key, history, message, payload, ttl=QNAChatbotService.QNA_TTL)

    @staticmethod
    def response_qna_list(user_id: int) -> list[LastQNAHistory]:
        keys = CacheRepository.get_qna_keys(user_id)
        qna_list = []
        for key, value in CacheRepository.get_many(keys).items():
            qna_list.append(CacheFactory.create_last_qna(key, value))

        return qna_list

    @staticmethod
    def make_qna_context(user_id: int, question_id: int) -> QNAChatbotContext:
        if not CacheRepository.get_session(SESSION_KEY.format(user_id=user_id)) == question_id:
            raise InactiveSessionException()
        initial = CacheRepository.get_initial(INITIAL_KEY.format(question_id=question_id))
        if initial is None:
            raise NotFoundException("해당 질문을 찾을 수 없습니다.")
        history = CacheRepository.get_history(QNA_KEY.format(user_id=user_id, question_id=question_id))
        if history is not None and len(history) >= 10:
            raise ConversationOverException()

        key = QNA_KEY.format(user_id=user_id, question_id=question_id)

        QNAChatbotService._make_session(user_id, question_id)

        return QNAChatbotContext(initial, history, key)

    @staticmethod
    def _return_qna_history(user_id: int, question_id: int, initial: InitialQNA) -> list[Message]:
        if CacheRepository.get_session(SESSION_KEY.format(user_id=user_id)) is None:
            QNAChatbotService._make_session(user_id, question_id)
        key = QNA_KEY.format(user_id=user_id, question_id=question_id)
        history = CacheRepository.get_history(key)
        if not history:
            initial_message = Message(role="assistant", content=initial.answer, created_at=str(initial.created_at))
            CacheRepository.save_history(key, [asdict(initial_message)], QNAChatbotService.QNA_TTL)
            history = [initial_message]
        return history

    @staticmethod
    def _make_session(user_id: int, question_id: int) -> None:
        CacheRepository.set_session(
            key=SESSION_KEY.format(user_id=user_id), value=question_id, ttl=QNAChatbotService.QNA_TTL
        )

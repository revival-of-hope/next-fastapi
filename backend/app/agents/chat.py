from collections.abc import Iterator

from sqlmodel import Session
from openai import Stream
from openai.types.responses import Response, ResponseStreamEvent
from app import crud
from app.models import ChatRequest, Conversation, MessageRole


class ConversationNotFoundError(Exception):
    """Raised when a conversation is absent or belongs to another user."""


class ChatBot:
    TITLE_LENGTH = 10
    DEFAULT_TITLE = "新对话"

    @staticmethod
    def _build_conversation_title(content: str) -> str:

        normalized_text = " ".join(content.split())
        if not normalized_text:
            return ChatBot.DEFAULT_TITLE

        return normalized_text[: ChatBot.TITLE_LENGTH]

    def prepare_chat(
        self,
        *,
        session: Session,
        user_id: int,
        request: ChatRequest,
    ) -> Conversation:
        if request.conversation_id is None:
            conversation = crud.create_conversation(
                session=session,
                user_id=user_id,
                title=self._build_conversation_title(request.content),
            )
        else:
            conversation = crud.get_conversation_for_user(
                session=session,
                conversation_id=request.conversation_id,
                user_id=user_id,
            )
            if conversation is None:
                raise ConversationNotFoundError
        crud.save_message(
            session=session,
            conversation=conversation,
            role=MessageRole.USER,
            content=request.content,
        )
        return conversation

    def stream_and_save(
        self,
        *,
        session: Session,
        conversation_id: int,
        chunks: Stream[ResponseStreamEvent],
    ) -> Iterator[str]:
        collected_chunks: list[str] = []
        reasoning_chunks: list[str] = []
        reasoning_started = False
        answer_started = False
        final_response: Response | None = None
        for event in chunks:
            if event.type == "response.output_text.delta":
                if not answer_started:
                    if reasoning_started:
                        yield "\n\n回答：\n"
                    answer_started = True
                collected_chunks.append(event.delta)
                yield event.delta
            elif event.type == "response.reasoning_text.delta":
                if not reasoning_started:
                    yield "思考：\n"
                    reasoning_started = True
                reasoning_chunks.append(event.delta)
                yield event.delta
            elif event.type == "response.completed":
                final_response = event.response
            elif event.type == "response.incomplete":
                final_response = event.response
            elif event.type == "error":
                raise RuntimeError(event.message)
            elif event.type == "response.failed":
                error = event.response.error
                raise RuntimeError(error.message if error else "Response failed")

        full_content = "".join(collected_chunks)
        if not full_content or not final_response or not final_response.usage:
            return
        usage = final_response.usage
        conversation = session.get(Conversation, conversation_id)
        if conversation is None:
            return
        crud.save_message(
            session=session,
            conversation=conversation,
            role=MessageRole.ASSISTANT,
            content=full_content,
            reasoning="".join(reasoning_chunks) or None,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            total_tokens=usage.total_tokens,
        )

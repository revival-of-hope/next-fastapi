from collections.abc import Iterator

from sqlmodel import Session
from openai import Stream
from openai.types.chat import ChatCompletionChunk
from app import crud
from app.models import ChatRequest, Conversation, MessageRole

TITLE_LENGTH = 10
DEFAULT_TITLE = "新对话"


class ConversationNotFoundError(Exception):
    """Raised when a conversation is absent or belongs to another user."""


class ChatBot:
    @staticmethod
    def _build_conversation_title(content: str) -> str:

        normalized_text = " ".join(content.split())
        if not normalized_text:
            return DEFAULT_TITLE

        return normalized_text[:TITLE_LENGTH]

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
        chunks: Stream[ChatCompletionChunk],
    ) -> Iterator[str]:
        collected_chunks: list[str] = []
        last_chunk: ChatCompletionChunk | None = None
        for chunk in chunks:
            last_chunk = chunk

            if not chunk.choices:
                continue
            content = chunk.choices[0].delta.content
            if content:
                collected_chunks.append(content)
                yield content

        full_content = "".join(collected_chunks)
        if not full_content or not last_chunk or not last_chunk.usage:
            return
        usage = last_chunk.usage
        conversation = session.get(Conversation, conversation_id)
        if conversation is None:
            return
        crud.save_message(
            session=session,
            conversation=conversation,
            role=MessageRole.ASSISTANT,
            content=full_content,
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
        )

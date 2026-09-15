from collections.abc import Iterator

from sqlmodel import Session

from app import crud
from app.core.db import engine
from app.models import ChatRequest, Conversation, MessageRole

TITLE_LENGTH = 10
DEFAULT_TITLE = "新对话"


class ConversationNotFoundError(Exception):
    """Raised when a conversation is absent or belongs to another user."""


def build_conversation_title(content: str) -> str:

    normalized_text = " ".join(content.split())
    if not normalized_text:
        return DEFAULT_TITLE

    return normalized_text[:TITLE_LENGTH]


def prepare_chat(
    *,
    session: Session,
    user_id: int,
    request: ChatRequest,
) -> Conversation:
    if request.conversation_id is None:
        conversation = crud.create_conversation(
            session=session,
            user_id=user_id,
            title=build_conversation_title(request.content),
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
    *,
    session: Session,
    conversation_id: int,
    chunks: Iterator[str],
) -> Iterator[str]:
    collected_chunks: list[str] = []

    for chunk in chunks:
        if not chunk:
            continue
        collected_chunks.append(chunk)
        yield chunk

    full_content = "".join(collected_chunks)

    if full_content:

        conversation = session.get(Conversation, conversation_id)
        if conversation is not None:
            crud.save_message(
                session=session,
                conversation=conversation,
                role=MessageRole.ASSISTANT,
                content=full_content,
            )

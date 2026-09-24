from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    ChatRequest,
    Conversation,
    ConversationPublic,
    Message,
    MessagePublic,
)
from app.agents.chat import ConversationNotFoundError, ChatBot
from app.agents.client import Agent

agent = Agent()
chatbot = ChatBot()

router = APIRouter(tags=["conversations"])

HISTORY_MESSAGE_LIMIT = 4


def _current_user_id(current_user: CurrentUser) -> int:
    if current_user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authenticated user",
        )
    return current_user.user_id


@router.get("/conversations", response_model=list[ConversationPublic])
def get_conversations(
    session: SessionDep,
    current_user: CurrentUser,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[Conversation]:
    conversations = crud.list_conversations(
        session=session,
        user_id=_current_user_id(current_user),
        offset=offset,
        limit=limit,
    )
    return list(conversations)


@router.get("/messages", response_model=list[MessagePublic])
def get_messages(
    conversation_id: Annotated[int, Query(ge=1)],
    session: SessionDep,
    current_user: CurrentUser,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> list[Message]:
    conversation = crud.get_conversation_for_user(
        session=session,
        conversation_id=conversation_id,
        user_id=_current_user_id(current_user),
    )
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = crud.list_messages(
        session=session,
        conversation_id=conversation_id,
        offset=offset,
        limit=limit,
    )
    return list(messages)


@router.post("/messages")
def chat(
    request: ChatRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> StreamingResponse:
    try:
        conversation = chatbot.prepare_chat(
            session=session,
            user_id=_current_user_id(current_user),
            request=request,
        )
    except ConversationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if conversation.conversation_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Conversation could not be created",
        )
    history = crud.get_history_message(
        session=session,
        conversation_id=conversation.conversation_id,
        # The current user message is already stored. Keep it plus four
        # preceding messages (two completed turns) in the model context.
        limit=HISTORY_MESSAGE_LIMIT + 1,
    )

    chunks = agent.stream_agent(
        history=history,
        enable_reasoning=request.enable_reasoning,
    )

    return StreamingResponse(
        chatbot.stream_and_save(
            session=session,
            conversation_id=conversation.conversation_id,
            chunks=chunks,
        ),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "X-Conversation-ID": str(conversation.conversation_id),
        },
    )

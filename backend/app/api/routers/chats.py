from typing import Annotated
import json
from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from app.domain.exceptions import (
    ConversationCreateError,
    ConversationNotFound,
)
from app.domain.schemas import ConversationPublic, ConversationsPublic, MessagesPublic
from app.services.deps import CurrentUserID, ChatServiceDep, SuperuserID

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("", status_code=status.HTTP_200_OK)
def get_conversations_list(
    service: ChatServiceDep,
    user_id: CurrentUserID,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 20,
) -> ConversationsPublic:
    return service.get_conversations(user_id, offset, limit)


@router.get("/messages", status_code=status.HTTP_200_OK)
def get_messages_list(
    service: ChatServiceDep,
    user_id: CurrentUserID,
    conversation_id: int,
) -> MessagesPublic:
    return service.get_messages(conversation_id, user_id)


@router.get("/usages", status_code=status.HTTP_200_OK)
def get_total_usages(_: SuperuserID, service: ChatServiceDep):
    return service.get_usages()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_conversation(
    service: ChatServiceDep, user_id: CurrentUserID, content: str
) -> ConversationPublic:
    try:
        conversation = service.post_conversation(user_id, content)
    except ConversationCreateError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation",
        )
    return conversation


@router.patch("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_title(
    user_id: CurrentUserID, service: ChatServiceDep, conversation_id: int, title: str
) -> None:
    try:
        service.update_conversation_title(user_id, conversation_id, title)
    except ConversationNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )


@router.post("/{conversation_id}", status_code=status.HTTP_200_OK)
def chat(
    service: ChatServiceDep,
    user_id: CurrentUserID,
    conversation_id: int,
    content: str,
    reasoning: str,
):
    try:
        stream = service.stream_and_save(
            user_id,
            conversation_id,
            content,
            reasoning,
        )
    except ConversationNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    return StreamingResponse(
        (f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n" for chunk in stream),
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
        media_type="text/event-stream",
    )

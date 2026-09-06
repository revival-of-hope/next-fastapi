from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Annotated, Any

from app.api.deps import SessionDep, CurrentUser
from app.utils.client import stream_agent
from app.models import Message, MessagePublic
from app import crud
from sqlmodel import select, desc

router = APIRouter(tags=["messages"])


# 新对话
@router.post("/messages")
async def chat(
    user_message: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> StreamingResponse:
    if not current_user.id:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user",
        )

    return StreamingResponse(
        stream_agent(current_user.id, user_message, session),
        headers={
            "Cache-Control": "no-cache",
        },
    )


# 消息列表
@router.get(
    "/me/messages",
    response_model=list[MessagePublic],
)
def get_chat_list(
    session: SessionDep,
    current_user: CurrentUser,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
) -> Any:
    statement = (
        select(Message)
        .where(Message.user_id == current_user.id)
        .order_by(desc(Message.created_at))
        .offset(offset=offset)
        .limit(limit=limit)
    )
    chatlist = session.exec(statement).all()
    return chatlist

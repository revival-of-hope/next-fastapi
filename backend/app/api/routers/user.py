from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Annotated, Any

from app.api.deps import SessionDep, CurrentUser
from app.utils.client import stream_agent
from app.models import ChatMessage, ChatMessagePublic, User, UserPublic, UserRegister
from app import crud
from sqlmodel import select, desc

router = APIRouter(prefix="/user", tags=["user"])


# response_model用于过滤密码
@router.post("/register", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    user = crud.get_user_by_name(session=session, name=user_in.name)
    if user:
        raise HTTPException(status_code=400, detail="Name exists")
    user_register = UserRegister.model_validate(user_in)
    user = crud.register_user(session=session, user_register=user_register)
    return user


# 用户主页
@router.get("/me", response_model=UserPublic)
def homepage(current_user: CurrentUser) -> User:
    return current_user


# 新对话
@router.post("/me/chat")
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
    response_model=list[ChatMessagePublic],
)
def get_chat_list(
    session: SessionDep,
    current_user: CurrentUser,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
) -> Any:
    statement = (
        select(ChatMessage)
        .where(ChatMessage.user_id == current_user.id)
        .order_by(desc(ChatMessage.created_at))
        .offset(offset=offset)
        .limit(limit=limit)
    )
    chatlist = session.exec(statement).all()
    return chatlist

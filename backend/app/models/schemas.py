from sqlmodel import SQLModel, Field
from datetime import datetime
from .tables import UserBase, MessageBase, ConversationBase


# User
class UserRegister(SQLModel):
    # 写成1是为了偷懒~
    name: str = Field(min_length=1, max_length=30)
    password: str = Field(min_length=1, max_length=15)


class UserPublic(UserBase):
    id: int
    created_at: datetime


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Message
class MessagePublic(MessageBase):
    message_id: int
    created_at: datetime


# Conversation
class ConversationPublic(ConversationBase):
    conversation_id: int
    created_at: datetime
    updated_at: datetime


# Request
class ChatRequest(SQLModel):
    # 根据id是否为空可以判断是否为已有对话
    conversation_id: int | None = Field(default=None, ge=1)
    content: str = Field(min_length=1, max_length=20_000)


# Token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str

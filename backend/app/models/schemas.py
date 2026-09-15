from enum import Enum
from sqlmodel import SQLModel, Field
from datetime import UTC, datetime
from .tables import UserBase, MessageBase, ConversationBase


# User
class UserPublic(UserBase):
    id: int
    created_at: datetime
    is_active: bool


class UserRegister(UserBase):
    # 写成1是为了偷懒~
    password: str = Field(min_length=1, max_length=15)


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


# 用于判断消息类型,从而区分用户提问和AI回答
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


# Token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str

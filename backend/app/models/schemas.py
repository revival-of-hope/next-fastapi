from sqlmodel import SQLModel, Field
from datetime import datetime
from .tables import UserBase, MessageBase, ConversationBase


# User
class UserRegister(SQLModel):
    # 写成1是为了偷懒~
    name: str = Field(min_length=1, max_length=30)
    password: str = Field(min_length=1, max_length=15)


class UserUsagePublic(SQLModel):
    """
    单个用户统计
    """

    # 对话次数统计
    messages_count: int = 0

    # Token 统计
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class UsagePublic(SQLModel):
    """
    总用户统计
    """

    messages_count: int = 0

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class UserPublic(UserBase):
    user_id: int
    created_at: datetime
    usage: UserUsagePublic | None = None


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
    enable_reasoning: bool = True


# Token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str

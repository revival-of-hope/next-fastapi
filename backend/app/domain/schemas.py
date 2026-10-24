from pydantic import BaseModel, Field
from tools import datetime
from app.domain.models import MessageRole, TokenUsage


# User
class UserRegister(BaseModel):
    # 写成1是为了偷懒~
    name: str = Field(min_length=1, max_length=30)
    password: str = Field(min_length=1, max_length=15)


class UserCreate(UserRegister):
    is_active: bool = True
    is_superuser: bool = False


class UserUsagePublic(BaseModel):
    """
    单个用户统计
    """

    # 对话次数统计
    messages_count: int = 0

    # Token 统计
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class UsagePublic(BaseModel):
    """
    总用户统计
    """

    messages_count: int = 0

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class UserPublic(BaseModel):
    name: str = Field(min_length=1, max_length=30)
    is_active: bool = True
    is_superuser: bool = False
    user_id: int
    created_at: datetime
    usage: UserUsagePublic | None = None


class UsersPublic(BaseModel):
    data: list[UserPublic]
    count: int


# Message
class MessagePublic(BaseModel):
    conversation_id: int | None
    role: MessageRole
    content: str
    reasoning: str | None = None

    message_id: int
    created_at: datetime


class MessagesPublic(BaseModel):
    data: list[MessagePublic]


# Conversation
class ConversationPublic(BaseModel):
    title: str | None = Field(
        default="新对话",
        min_length=1,
        max_length=120,
    )
    conversation_id: int
    created_at: datetime
    updated_at: datetime


class ConversationsPublic(BaseModel):
    data: list[ConversationPublic]


# Agent
class ResponsePublic(BaseModel):
    output_text: str
    usage: TokenUsage


# Token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str

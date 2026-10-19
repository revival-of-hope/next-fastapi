from enum import Enum
from pydantic import BaseModel, Field
from tools import get_datetime, datetime


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class User(BaseModel):
    name: str
    hashed_password: str
    user_id: int | None = None
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=get_datetime)


class TokenUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class UserUsage(TokenUsage):
    user_id: int
    messages_count: int = 0


class Conversation(BaseModel):
    user_id: int
    conversation_id: int | None = None
    title: str | None = "新对话"
    created_at: datetime = Field(default_factory=get_datetime)
    updated_at: datetime = Field(default_factory=get_datetime)


class Message(BaseModel):
    conversation_id: int | None
    role: MessageRole
    content: str
    message_id: int | None = None
    reasoning: str | None = None
    created_at: datetime = Field(default_factory=get_datetime)

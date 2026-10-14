from dataclasses import dataclass, field
from enum import Enum
from tools import get_datetime, datetime


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class UserDomain:
    name: str
    hashed_password: str
    user_id: int | None = None
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = field(default_factory=get_datetime)


@dataclass
class UserUsage:
    user_id: int
    messages_count: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


@dataclass
class Conversation:
    user_id: int
    conversation_id: int | None = None
    title: str | None = "新对话"
    created_at: datetime = field(default_factory=get_datetime)
    updated_at: datetime = field(default_factory=get_datetime)


@dataclass
class Message:
    conversation_id: int | None
    role: MessageRole
    content: str
    message_id: int | None = None
    reasoning: str | None = None
    created_at: datetime = field(default_factory=get_datetime)

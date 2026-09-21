from enum import Enum
from sqlmodel import Relationship, SQLModel, Field, Text
from datetime import UTC, datetime


def get_datetime() -> datetime:
    return datetime.now(UTC)


# 用于判断消息类型,从而区分用户提问和AI回答
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


# User
class UserBase(SQLModel):
    name: str = Field(
        min_length=1,
        max_length=30,
        index=True,
    )
    is_active: bool = True
    is_superuser: bool = False


class User(UserBase, table=True):
    user_id: int | None = Field(default=None, primary_key=True)
    hashed_password: str = Field(max_length=256)
    created_at: datetime = Field(default_factory=get_datetime)
    conversations: list["Conversation"] = Relationship(
        back_populates="user",
        cascade_delete=True,
    )

    usage: "UserUsage" = Relationship(back_populates="user", cascade_delete=True)


class UserUsage(SQLModel, table=True):
    user_id: int = Field(
        foreign_key="user.user_id",
        primary_key=True,
        ondelete="CASCADE",
    )

    # 对话次数统计
    messages_count: int = 0

    # Token 统计
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    user: User = Relationship(back_populates="usage")


# Conversation
class ConversationBase(SQLModel):
    title: str | None = Field(default="新对话", min_length=1, max_length=120)


class Conversation(ConversationBase, table=True):
    conversation_id: int | None = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.user_id")
    user: User | None = Relationship(back_populates="conversations")

    messages: list["Message"] = Relationship(
        back_populates="conversation",
        cascade_delete=True,
    )
    created_at: datetime = Field(
        default_factory=get_datetime,
    )
    updated_at: datetime = Field(
        default_factory=get_datetime,
    )


# Message


class MessageBase(SQLModel):
    conversation_id: int | None = Field(
        foreign_key="conversation.conversation_id",
        ondelete="CASCADE",
    )
    role: MessageRole
    # sa_type表示强制让引擎把content的类型改为Text,
    # 从而可以支持存储AI输出的冗长文本
    content: str = Field(sa_type=Text, nullable=False)


class Message(MessageBase, table=True):
    message_id: int = Field(
        default=None,
        primary_key=True,
    )
    created_at: datetime = Field(default_factory=get_datetime)
    conversation: Conversation | None = Relationship(
        back_populates="messages",
    )

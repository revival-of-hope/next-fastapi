from enum import Enum
from sqlmodel import Relationship, SQLModel, Field, Text
from tools import datetime, get_datetime
from domain.models import MessageRole


# User
class UserRecord(SQLModel, table=True):
    name: str = Field(
        min_length=1,
        max_length=30,
        index=True,
    )
    is_active: bool = True
    is_superuser: bool = False
    user_id: int | None = Field(default=None, primary_key=True)
    hashed_password: str = Field(max_length=256)
    created_at: datetime = Field(default_factory=get_datetime)
    conversations: list["ConversationRecord"] = Relationship(
        back_populates="user",
        cascade_delete=True,
    )

    usage: "UserUsageRecord" = Relationship(back_populates="user", cascade_delete=True)


class UserUsageRecord(SQLModel, table=True):
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

    user: UserRecord = Relationship(back_populates="usage")


# Conversation
class ConversationRecord(SQLModel, table=True):
    title: str | None = Field(default="新对话", min_length=1, max_length=120)
    conversation_id: int | None = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.user_id")
    user: UserRecord | None = Relationship(back_populates="conversations")

    messages: list["MessageRecord"] = Relationship(
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
class MessageRecord(SQLModel, table=True):
    conversation_id: int | None = Field(
        foreign_key="conversation.conversation_id",
        ondelete="CASCADE",
    )
    role: MessageRole
    # sa_type表示强制让引擎把content的类型改为Text,
    # 从而可以支持存储AI输出的冗长文本
    content: str = Field(sa_type=Text, nullable=False)
    reasoning: str | None = Field(default=None, sa_type=Text)

    message_id: int = Field(
        default=None,
        primary_key=True,
    )
    created_at: datetime = Field(default_factory=get_datetime)
    conversation: ConversationRecord | None = Relationship(
        back_populates="messages",
    )

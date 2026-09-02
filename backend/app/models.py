from pydantic import BaseModel
from sqlalchemy import DateTime
from sqlmodel import Relationship, SQLModel, Field, Text
from datetime import UTC, datetime


def get_datetime() -> datetime:
    return datetime.now(UTC)


# User


class UserBase(SQLModel):
    name: str = Field(default=None, min_length=1, max_length=30)


class UserRegister(UserBase):
    # 写成1是为了偷懒~
    password: str = Field(min_length=1, max_length=15)


class UserPublic(UserBase):
    id: int
    created_at: datetime
    is_active: bool = True


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str = Field(max_length=256)
    is_active: bool = True
    created_at: datetime = Field(default_factory=get_datetime)
    conversations: list["Conversation"] = Relationship(
        back_populates="user",
        cascade_delete=True,
    )


# Conversation
class ConversationCreate(SQLModel):
    title: str | None = Field(default=None, max_length=120)


class ConversationBase(SQLModel):
    title: str = Field(max_length=35)
    conversation_id: int | None = Field(default=None, primary_key=True)


class ConversationPublic(ConversationBase):
    created_at: datetime
    updated_at: datetime


class Conversation(ConversationBase, table=True):
    created_at: datetime = Field(
        default_factory=get_datetime,
    )
    update_at: datetime = Field(
        default_factory=get_datetime,
    )
    user_id: int | None = Field(foreign_key="user.id")

    user: User | None = Relationship(back_populates="conversations")
    messages: list["Message"] = Relationship(
        back_populates="conversation",
        cascade_delete=True,
    )


# Message
class MessageRole(BaseModel):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ChatRequest(SQLModel):
    # 根据id是否为空可以判断是否为已有对话
    conversation_id: int | None = None
    content: str = Field(min_length=3)


class MessageBase(SQLModel):
    message_id: int | None = Field(
        default=None,
        primary_key=True,
    )
    conversation_id: int = Field(
        foreign_key="conversation.conversation_id",
        ondelete="CASCADE",
    )
    role: MessageRole
    # sa_type表示强制让引擎把content的类型改为Text,
    # 从而可以支持存储AI输出的冗长文本
    content: str = Field(sa_type=Text, nullable=False)


class MessagePublic(MessageBase):
    created_at: datetime


class Message(MessageBase, table=True):

    created_at: datetime = Field(default_factory=get_datetime)
    conversation: Conversation | None = Relationship(
        back_populates="messages",
    )


class ConversationDetail(ConversationPublic):
    messages: list[MessagePublic] = Field(default_factory=list)


# Token


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str

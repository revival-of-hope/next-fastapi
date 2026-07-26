from sqlalchemy import DateTime
from sqlmodel import Relationship, SQLModel, Field
from datetime import UTC, datetime


def get_datetime() -> datetime:
    return datetime.now(UTC)


class UserBase(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class UserRegister(SQLModel):
    password: str
    name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=16)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime,
    )
    chats: list["ChatMessage"] = Relationship(
        back_populates="user",
        cascade_delete=True,
    )


class Message(SQLModel):
    message: str


class ChatMessage(SQLModel, table=True):
    chat_id: int | None = Field(default=None, primary_key=True)
    content: str | None = None
    created_at: datetime | None = Field(
        default_factory=get_datetime,
    )
    user_id: int | None = Field(foreign_key="user.id")
    user: User | None = Relationship(back_populates="chats")


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None

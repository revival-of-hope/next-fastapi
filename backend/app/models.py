from sqlmodel import Relationship, SQLModel, Field


class UserBase(SQLModel):
    name: str


class UserRegister(UserBase):
    password: str


class UserLogin(UserBase):
    password: str


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    chat: list["ChatMessage"] = Relationship(
        back_populates="user",
        cascade_delete=True,
    )


class Message(SQLModel):
    message: str


class ChatMessage(SQLModel, table=True):
    chat_id: int | None = Field(default=None, primary_key=True)
    content: str | None = None
    user_id: int | None = Field(foreign_key="user.id")
    user: User | None = Relationship(back_populates="chat")

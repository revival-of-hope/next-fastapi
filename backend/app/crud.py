from app.core.security import (
    verify_password,
    hashing_password,
)
from fastapi import HTTPException
from sqlmodel import Session, select
from app.models import User, UserCreate, UserRegister, ChatMessage

# Dummy hash to use for timing attack prevention when user is not found
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"


def check_db(*, session: Session):
    result = session.exec(select(1)).one()
    return result == 1


def register_user(*, session: Session, user_register: UserRegister) -> User:
    user_store = User.model_validate(
        user_register,
        update={"hashed_password": hashing_password(user_register.password)},
    )

    session.add(user_store)
    session.commit()
    session.refresh(user_store)

    return user_store


def get_user_by_name(*, session: Session, name: str) -> User | None:
    statement = select(User).where(User.name == name)
    user = session.exec(statement).first()
    return user


def check_user(session: Session, name: str, password: str) -> User | None:
    db_user = get_user_by_name(session=session, name=name)
    if not db_user:
        verify_password(password, DUMMY_HASH)
        return None
    verified = verify_password(password, db_user.hashed_password)
    if not verified:
        return None
    return db_user


# 工具函数
def save_chat_message(
    *, session: Session, user_id: int | None, content: str
) -> ChatMessage:
    message = ChatMessage(
        user_id=user_id,
        content=content,
    )
    session.add(message)
    session.commit()
    session.refresh(message)

    return message


def stream_and_save(*, session: Session, user_id: int | None, chunks):
    collected_chunks: list[str] = []
    for chunk in chunks:
        if not chunk:
            continue
        collected_chunks.append(chunk)
        yield chunk
    full_content = "".join(collected_chunks)
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")
    if full_content:
        save_chat_message(
            user_id=user_id,
            content=full_content,
            session=session,
        )

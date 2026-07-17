from app.utils.security import (
    verify_password,
    hashing_password,
)
from fastapi import HTTPException
from sqlmodel import Session, select
from app.models import User, UserLogin, UserRegister, ChatMessage


def healthchecker(session: Session):
    result = session.exec(select(1)).one()
    return result == 1


def register_user(session: Session, user_create: UserRegister) -> User:
    user_store = User.model_validate(
        user_create, update={"hashed_password": hashing_password(user_create.password)}
    )
    # 数据库存储
    session.add(user_store)
    session.commit()
    session.refresh(user_store)

    # 返回信息供路由函数处理
    return user_store


def check_user(session: Session, user_login: UserLogin, user_db: User):
    user = session.exec(select(User).where(user_login.name == user_db.name)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(UserLogin.password, User.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return user


def save_chat_message(session: Session, user_id: int, content: str) -> ChatMessage:
    message = ChatMessage(
        user_id=user_id,
        content=content,
    )
    session.add(message)
    session.commit()
    session.refresh(message)

    return message


def stream_and_save(chunks, user_id: int, session: Session):
    collected_chunks: list[str] = []
    for chunk in chunks:
        if not chunk:
            continue
        collected_chunks.append(chunk)
        yield chunk
    full_content = "".join(collected_chunks)
    if full_content:
        save_chat_message(
            user_id=user_id,
            content=full_content,
            session=session,
        )

from typing import List
from app.core.security import (
    verify_password,
    hashing_password,
)
from sqlmodel import Session, select, desc
from app.models import (
    Message,
    MessageRole,
    User,
    UserRegister,
    Conversation,
    get_datetime,
)

# Dummy hash to use for timing attack prevention when user is not found
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"


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


# 保存消息
def save_message(
    *,
    session: Session,
    conversation: Conversation,
    role: MessageRole,
    content: str,
) -> Message:
    message = Message(
        conversation_id=conversation.conversation_id,
        role=role,
        content=content,
    )
    conversation.updated_at = get_datetime()
    session.add(message)
    session.add(conversation)
    session.commit()
    session.refresh(message)

    return message


# 获取历史消息
def get_history_message(
    *,
    session: Session,
    conversation: Conversation,
    limit: int = 4,
) -> List[Message]:
    id = conversation.conversation_id
    if id is None:
        return []
    statement = (
        select(Message)
        .where(Message.conversation_id == id)
        .order_by(
            desc(Message.created_at),
            desc(Message.message_id),
        )
        .limit(limit)
    )
    messages = list(session.exec(statement).all())
    messages.reverse()
    return messages

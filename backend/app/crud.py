from app.core.security import verify_password, hashing_password
from sqlmodel import Session, select, desc, asc, func
from sqlalchemy.orm import selectinload
from app.models import (
    Message,
    MessageRole,
    User,
    UserRegister,
    UserUsage,
    Conversation,
    UsagePublic,
    get_datetime,
)
from app.models.schemas import UserCreate, UserPublic, UsersPublic

# Dummy hash to use for timing attack prevention when user is not found
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"


def register_user(
    *, session: Session, user_register: UserRegister | UserCreate
) -> User:
    user = User.model_validate(
        user_register,
        update={"hashed_password": hashing_password(user_register.password)},
    )
    try:
        session.add(user)
        session.flush()
        if user.user_id is None:
            raise RuntimeError("Failed to generate user_id")

        usage = UserUsage(user_id=user.user_id)

        session.add(usage)
        session.commit()

    except Exception:
        session.rollback()
        raise

    session.refresh(user)
    return user


def get_user_by_name(*, session: Session, name: str) -> User | None:
    return session.exec(select(User).where(User.name == name)).first()


def check_user(*, session: Session, name: str, password: str) -> User | None:
    db_user = get_user_by_name(session=session, name=name)
    if not db_user:
        verify_password(password, DUMMY_HASH)
        return None
    verified = verify_password(password, db_user.hashed_password)
    if not verified:
        return None
    return db_user


def get_users(*, session: Session, offset: int, limit: int) -> UsersPublic:
    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = (
        select(User)
        .options(selectinload(User.usage))  # type: ignore
        .order_by(
            desc(User.created_at),
            desc(User.user_id),
        )
        .offset(offset)
        .limit(limit)
    )
    users = session.exec(statement).all()

    users_public = [UserPublic.model_validate(user) for user in users]
    return UsersPublic(data=users_public, count=count)


def get_usage_totals(*, session: Session) -> UsagePublic:
    # 长这么丑我也很无奈
    statement = select(
        func.coalesce(func.sum(UserUsage.messages_count), 0),
        func.coalesce(func.sum(UserUsage.input_tokens), 0),
        func.coalesce(func.sum(UserUsage.output_tokens), 0),
        func.coalesce(func.sum(UserUsage.total_tokens), 0),
    )

    result = session.exec(statement).one()

    return UsagePublic(
        messages_count=int(result[0]),
        input_tokens=int(result[1]),
        output_tokens=int(result[2]),
        total_tokens=int(result[3]),
    )


def create_conversation(
    *,
    session: Session,
    user_id: int,
    title: str,
) -> Conversation:
    conversation = Conversation(user_id=user_id, title=title)

    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def get_conversation_for_user(
    *,
    session: Session,
    conversation_id: int,
    user_id: int,
) -> Conversation | None:
    statement = select(Conversation).where(
        Conversation.conversation_id == conversation_id,
        Conversation.user_id == user_id,
    )
    result = session.exec(statement).first()
    return result


def list_conversations(
    *,
    session: Session,
    user_id: int,
    offset: int = 0,
    limit: int = 20,
) -> list[Conversation]:
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(
            desc(Conversation.updated_at),
            desc(Conversation.conversation_id),
        )
        .offset(offset)
        .limit(limit)
    )
    result = session.exec(statement).all()
    return list(result)


def save_message(
    *,
    session: Session,
    conversation: Conversation,
    role: MessageRole,
    content: str,
    reasoning: str | None = None,
    input_tokens: int = 0,
    output_tokens: int = 0,
    total_tokens: int = 0,
) -> Message:
    if conversation.conversation_id is None:
        raise ValueError("Conversation must be persisted before saving messages")

    message = Message(
        conversation_id=conversation.conversation_id,
        role=role,
        content=content,
        reasoning=reasoning,
    )
    conversation.updated_at = get_datetime()

    if role == MessageRole.ASSISTANT:
        usage = session.get(UserUsage, conversation.user_id)

        if usage is None:
            usage = UserUsage(user_id=conversation.user_id)
            session.add(usage)

        usage.messages_count += 1
        usage.input_tokens += input_tokens
        usage.output_tokens += output_tokens
        usage.total_tokens += total_tokens
    try:
        session.add(message)
        session.add(conversation)
        session.commit()
    except Exception:
        session.rollback()
        raise

    session.refresh(message)
    return message


def list_messages(
    *,
    session: Session,
    conversation_id: int,
    offset: int = 0,
    limit: int = 100,
) -> list[Message]:
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(
            asc(Message.created_at),
            asc(Message.message_id),
        )
        .offset(offset)
        .limit(limit)
    )
    result = list(session.exec(statement).all())
    return result


def get_history_message(
    *,
    session: Session,
    conversation_id: int,
    limit: int = 4,
) -> list[Message]:
    if limit < 1:
        return []

    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(
            desc(Message.created_at),
            desc(Message.message_id),
        )
        .limit(limit)
    )
    messages = list(session.exec(statement).all())
    messages.reverse()
    return messages

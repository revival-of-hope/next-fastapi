from abc import abstractmethod, ABC
from sqlmodel import Session, select, desc
from sqlalchemy.orm import selectinload

from app.domain.models import Conversation, MessageRole, TokenUsage, User, UserUsage
from app.domain.schemas import (
    ConversationPublic,
    ConversationsPublic,
    MessagePublic,
    MessagesPublic,
    UserPublic,
    UsersPublic,
    UserRegister,
)
from app.models import UserRecord, mapper, ConversationRecord, MessageRecord
from app.core.security import verify_password, hashing_password
from app.infra.datas import add_usage, users_amount, DUMMY_HASH, HISTORY_MESSAGE_LIMIT
from app.tools import get_datetime


class AbstractRepo(ABC):
    def __init__(self, session: Session):
        self._session = session

    @abstractmethod
    def get(self): ...

    @abstractmethod
    def get_all(self): ...

    @abstractmethod
    def post(self): ...


class UserRepo(AbstractRepo):
    def get(self, name: str) -> User | None:
        statement = select(UserRecord).where(UserRecord.name == name)
        userrecord = self._session.exec(statement).one()

        if userrecord is None:
            raise

        return mapper(userrecord, User)

    def get_all(self, offset: int, limit: int) -> UsersPublic:
        statement = (
            select(UserRecord)
            .options(selectinload(UserRecord.usage))  # type: ignore
            .order_by(
                desc(UserRecord.created_at),
                desc(UserRecord.user_id),
            )
            .offset(offset)
            .limit(limit)
        )
        users = self._session.exec(statement).all()

        users_public: list = []
        for user in users:
            users_public.append(UserPublic.model_validate(user))

        return UsersPublic(
            data=users_public,
            count=users_amount(self._session),
        )

    def post(self, user_in: UserRegister) -> UserPublic:
        user = UserRecord.model_validate(
            user_in,
            update={"hashed_password": hashing_password(user_in.password)},
        )

        try:
            self._session.add(user)
            self._session.flush()
            if user.user_id is None:
                raise Exception
            usage = UserUsage(user_id=user.user_id)

        except Exception:
            self._session.rollback()
            raise

        self._session.refresh(user)
        return UserPublic.model_validate(user)

    def delete(self, user_id: int) -> None:
        userrecord = self._session.get(UserRecord, user_id)

        if not userrecord:
            raise
        try:
            self._session.delete(userrecord)
            self._session.commit()
        except:
            self._session.rollback()
            raise

    def check(self, name: str, password: str) -> int | None:
        db_user = self.get(name)

        if db_user is None:
            verify_password(password, DUMMY_HASH)
            raise Exception

        verified = verify_password(password, db_user.hashed_password)
        if not verified:
            raise Exception

        return db_user.user_id


class ConversationRepo(AbstractRepo):
    def get(self, conversation_id: int, user_id: int):
        statement = select(ConversationRecord).where(
            ConversationRecord.conversation_id == conversation_id,
            ConversationRecord.user_id == user_id,
        )
        conversation = self._session.exec(statement).one()
        return mapper(conversation, Conversation)

    def get_all(self, user_id: int, offset=0, limit: int = 50) -> ConversationsPublic:
        statement = (
            select(ConversationRecord)
            .where(ConversationRecord.user_id == user_id)
            .order_by(
                desc(ConversationRecord.updated_at),
                desc(ConversationRecord.conversation_id),
            )
            .offset(offset)
            .limit(limit)
        )
        results = self._session.exec(statement).all()
        lists = [mapper(result, ConversationPublic) for result in results]
        return ConversationsPublic(data=lists)

    def post(self, user_id: int, title: str) -> ConversationPublic:
        conversation = ConversationRecord(user_id=user_id, title=title)

        self._session.add(conversation)
        self._session.commit()
        self._session.refresh(conversation)
        return ConversationPublic.model_validate(conversation)

    def post_usage(
        self, user_id: int, tokenusage: TokenUsage, role: MessageRole
    ) -> None:
        # 用量计算
        usage = self._session.get(UserUsage, user_id)
        if usage is None:
            usage = UserUsage(user_id=user_id)
            self._session.add(usage)
        add_usage(usage, tokenusage, role)

        self._session.commit()

    def post_message(
        self,
        conversation_id: int,
        role: MessageRole,
        content: str,
        reasoning: str | None = None,
    ) -> None:
        # 对话保存
        message = MessageRecord(
            conversation_id=conversation_id,
            role=role,
            content=content,
            reasoning=reasoning,
        )

        # 更新对话的最新更新时间
        conversation = self._session.get(ConversationRecord, conversation_id)
        if conversation is None:
            raise Exception

        conversation.updated_at = get_datetime()
        try:
            self._session.add(message)
            self._session.add(conversation)
            self._session.commit()
        except:
            self._session.rollback()
            raise

    def get_messages(
        self,
        conversation_id: int,
        user_id: int,
        offset: int = 0,
        limit: int = HISTORY_MESSAGE_LIMIT,
    ) -> MessagesPublic:
        statement = (
            select(MessageRecord)
            .join(ConversationRecord)
            .where(
                ConversationRecord.conversation_id == conversation_id,
                Conversation.user_id == user_id,
            )
            .order_by(
                desc(MessageRecord.created_at),
                desc(MessageRecord.message_id),
            )
            .offset(offset)
            .limit(limit)
        )
        lists = list(self._session.exec(statement).all())
        lists.reverse()
        messages = [MessagePublic.model_validate(message) for message in lists]

        return MessagesPublic(data=messages)

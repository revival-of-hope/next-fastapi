from abc import abstractmethod, ABC
from sqlmodel import Session, select, desc
from sqlalchemy.orm import selectinload

from app.domain.exceptions import (
    AddError,
    CommitError,
    ConversationRecordCreateError,
    ConversationRecordNotFound,
    ConversationsRecordNotFound,
    DbException,
    DeleteError,
    UserAddError,
    UserDeleteError,
    UserNameNotFound,
    UserRecordCreateFailed,
    UserRecordDeleteError,
    UserRecordNotFound,
    UsersRecordNotFound,
    VerifyError,
)
from app.domain.models import Conversation, MessageRole, TokenUsage, User, UserUsage
from app.domain.schemas import (
    ConversationPublic,
    ConversationsPublic,
    MessagePublic,
    MessagesPublic,
    UsagePublic,
    UserPublic,
    UsersPublic,
    UserRegister,
)
from app.models import UserRecord, mapper, ConversationRecord, MessageRecord
from app.core.security import verify_password, hashing_password
from app.core.config import settings
from app.infra.datas import (
    add_usage,
    get_usage_totals,
    users_amount,
    build_conversation_title,
    DUMMY_HASH,
)
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
            raise UserRecordNotFound("User Record Not Found")

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

        if not users:
            raise UsersRecordNotFound("Users Record Not Found")

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
                raise UserRecordCreateFailed("User Record Create Failed")

        except UserRecordCreateFailed:
            self._session.rollback()
            raise

        self._session.refresh(user)
        return UserPublic.model_validate(user)

    def delete(self, user_id: int) -> None:
        userrecord = self._session.get(UserRecord, user_id)

        if not userrecord:
            raise UsersRecordNotFound("Users Record Not Found")
        try:
            self._session.delete(userrecord)
            self._session.commit()
        except CommitError, DeleteError:
            self._session.rollback()
            raise UserRecordDeleteError("user record delete failed")

    def check(self, name: str, password: str) -> int | None:
        db_user = self.get(name)

        if db_user is None:
            verify_password(password, DUMMY_HASH)
            raise UserNameNotFound("Username Not Found")

        verified = verify_password(password, db_user.hashed_password)
        if not verified:
            raise VerifyError("vecification failed")

        return db_user.user_id


class ConversationRepo(AbstractRepo):
    def get(self, conversation_id: int, user_id: int) -> Conversation:
        statement = select(ConversationRecord).where(
            ConversationRecord.conversation_id == conversation_id,
            ConversationRecord.user_id == user_id,
        )
        conversation = self._session.exec(statement).one()
        if not conversation:
            raise ConversationRecordNotFound("Conversation Record Not Found")
        return mapper(conversation, Conversation)

    def get_all(
        self, user_id: int, offset: int = 0, limit: int = 50
    ) -> ConversationsPublic:
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
        if not results:
            raise ConversationsRecordNotFound("Conversations Record Not Found")
        lists = [mapper(result, ConversationPublic) for result in results]
        return ConversationsPublic(data=lists)

    def post(self, user_id: int, content: str) -> ConversationPublic:
        title = build_conversation_title(content)
        conversation = ConversationRecord(user_id=user_id, title=title)
        try:
            self._session.add(conversation)
            self._session.commit()
            self._session.refresh(conversation)
        except AddError, CommitError:
            raise ConversationRecordCreateError("Conversation record create failed")

        return ConversationPublic.model_validate(conversation)

    def update_title(self, conversation_id: int, title: str) -> None:
        conversationrecord = self._session.get(ConversationRecord, conversation_id)
        if not conversationrecord:
            raise Exception
        conversationrecord.title = title
        try:
            self._session.add(conversationrecord)
            self._session.commit()
        except:
            self._session.rollback()
            raise Exception

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
    ) -> None:
        # 对话保存
        message = MessageRecord(
            conversation_id=conversation_id,
            role=role,
            content=content,
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
            raise Exception

    def get_messages(
        self,
        conversation_id: int,
        user_id: int,
        offset: int = 0,
        limit: int = settings.HISTORY_MESSAGE_LIMIT,
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

    def get_usages(self) -> UsagePublic:
        return get_usage_totals(self._session)

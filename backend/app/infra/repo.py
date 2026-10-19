from abc import abstractmethod, ABC
from sqlmodel import Session, select, desc
from sqlalchemy.orm import selectinload

from app.domain.models import Conversation, User, UserUsage
from app.domain.schemas import (
    ConversationPublic,
    ConversationsPublic,
    UserPublic,
    UsersPublic,
    UserRegister,
)
from app.models import UserRecord, mapper, ConversationRecord
from app.core.security import verify_password, hashing_password
from app.infra.datas import users_amount, DUMMY_HASH


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
        user = self._session.exec(statement).one()
        if user is None:
            return None

        return mapper(user, User)

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

    def post_message(self,conversation_id:int,user_id:int,)

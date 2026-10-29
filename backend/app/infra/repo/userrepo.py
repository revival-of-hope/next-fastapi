from sqlmodel import select, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.domain.exceptions import (
    PasswordMatchError,
    UserRecordDeleteError,
    UserRecordNotFound,
    UsersRecordNotFound,
)
from app.domain.models import User
from app.domain.schemas import (
    UserPublic,
    UsersPublic,
    UserRegister,
)
from app.models import UserRecord, mapper
from app.core.security import verify_password, hashing_password
from app.infra.datas import (
    users_amount,
    DUMMY_HASH,
)
from app.infra.repo.abstractrepo import AbstractRepo


class UserRepo(AbstractRepo):
    def get_by_id(self, user_id: int) -> User:
        statement = select(UserRecord).where(UserRecord.user_id == user_id)
        userrecord = self._session.exec(statement).first()
        if userrecord is None:
            raise UserRecordNotFound("User Record Not Found")

        return mapper(userrecord, User)

    def get_by_name(self, name: str) -> User:
        statement = select(UserRecord).where(UserRecord.name == name)

        userrecord = self._session.exec(statement).first()

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
        users_public: list = []

        for user in users:
            users_public.append(mapper(user, UserPublic))

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

            self._session.commit()

        except SQLAlchemyError:
            self._session.rollback()
            raise

        self._session.refresh(user)
        return mapper(user, UserPublic)

    def delete(self, user_id: int) -> None:
        userrecord = self._session.get(UserRecord, user_id)

        if not userrecord:
            raise UsersRecordNotFound("Users Record Not Found")
        try:
            self._session.delete(userrecord)
            self._session.commit()
        except SQLAlchemyError as e:
            self._session.rollback()
            raise UserRecordDeleteError("user record delete failed") from e

    def check(self, name: str, password: str) -> int | None:
        db_user = self.get_by_name(name)

        if db_user is None:
            verify_password(password, DUMMY_HASH)
            raise UserRecordNotFound("User record Not Found")

        verified = verify_password(password, db_user.hashed_password)
        if not verified:
            raise PasswordMatchError("Password Don't Match")

        return db_user.user_id

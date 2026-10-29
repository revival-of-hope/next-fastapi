from app.domain.exceptions import (
    PasswordMatchError,
    UserCreateError,
    UserDeleteError,
    UserNotFound,
    UserRecordCreateFailed,
    UserRecordDeleteError,
    UserRecordNotFound,
    UsersNotFound,
    UsersRecordNotFound,
)
from app.services.baseservice import BaseService
from app.infra.repo import UserRepo
from app.domain.schemas import UserPublic, UserRegister, UsersPublic
from app.models.mappers import mapper


class UserService(BaseService[UserRepo]):
    def get_by_id(self, user_id: int) -> UserPublic:
        try:
            user = self._repo.get_by_id(user_id)
        except UserRecordNotFound:
            raise UserNotFound("User not found")

        return mapper(user, UserPublic)

    def get_by_name(self, name: str) -> UserPublic:
        try:
            user = self._repo.get_by_name(name)
        except UserRecordNotFound:
            raise UserNotFound("User not found")

        return mapper(user, UserPublic)

    def get_all(self, offset: int, limit: int) -> UsersPublic:
        return self._repo.get_all(offset, limit)

    def post(self, user_in: UserRegister) -> UserPublic:
        try:
            user = self._repo.post(user_in)
        except UserRecordCreateFailed:
            raise UserCreateError("Fail to create new user")
        return user

    def delete(self, user_id: int) -> None:
        try:
            self._repo.delete(user_id)
        except UserRecordDeleteError:
            raise UserDeleteError("Fail to delete user")
        except UsersRecordNotFound:
            raise UserNotFound("User not found")

    def check(self, name: str, password: str) -> int | None:
        try:
            user_id = self._repo.check(name, password)
        except UserRecordNotFound:
            raise UserNotFound("User not found")
        except PasswordMatchError:
            raise
        return user_id

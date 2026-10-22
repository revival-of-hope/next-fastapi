from app.services.baseservice import BaseService
from app.infra.repo import UserRepo
from app.domain.schemas import UserPublic, UserRegister, UsersPublic


class UserService(BaseService[UserRepo]):
    def get(self, name: str) -> UserPublic:
        user = self._repo.get(name)
        if not user:
            raise
        return UserPublic.model_validate(user)

    def get_all(self, offset: int, limit: int) -> UsersPublic:
        users = self._repo.get_all(offset, limit)

        return users

    def post(self, user_in: UserRegister) -> UserPublic:
        user = self._repo.post(user_in)
        if not user:
            raise
        return user

    def delete(self, user_id: int) -> None:
        try:
            self._repo.delete(user_id)
        except:
            raise

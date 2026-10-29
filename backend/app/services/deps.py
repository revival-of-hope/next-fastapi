from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
import jwt
from typing import Annotated, Generator
from sqlmodel import Session

from app.core.db import engine
from app.domain.models import User
from app.domain.schemas import TokenPayload
from app.core.config import settings
from app.core.security import ALGORITHM
from app.models import UserRecord
from app.models.mappers import mapper
from app.infra.repo import UserRepo, ConversationRepo
from app.services import UserService, ChatService

oauth2 = OAuth2PasswordBearer(tokenUrl="api/auth/access-token", scheme_name="Oauth2")

TokenDep = Annotated[str, Depends(oauth2)]


def get_db() -> Generator[Session]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


def get_user_service(session: SessionDep) -> UserService:
    repo = UserRepo(session)
    return UserService(repo)


def get_chat_service(session: SessionDep) -> ChatService:
    repo = ConversationRepo(session)
    return ChatService(repo)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]


def get_current_user(
    session: SessionDep,
    token: TokenDep,
) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        # payload带有sub(用户ID)和exp等字段,但我们只需要sub即可
        sub = TokenPayload(**payload).sub
        user_id = int(sub)
    except (jwt.InvalidTokenError, ValueError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from e

    userrecord = session.get(UserRecord, user_id)

    if userrecord is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
        )

    return mapper(userrecord, User)


def get_current_user_id(user: Annotated[User, Depends(get_current_user)]) -> int | None:
    return user.user_id


CurrentUserID = Annotated[int, Depends(get_current_user_id)]


def get_current_superuser_id(
    user: Annotated[User, Depends(get_current_user)],
) -> int | None:
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    return user.user_id


SuperuserID = Annotated[int, Depends(get_current_superuser_id)]

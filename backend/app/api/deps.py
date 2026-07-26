from collections.abc import Generator
from typing import Annotated

from sqlmodel import Session

from app.core.db import engine
from app.models import User, TokenPayload  # newline
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status  # newline

# newline
import jwt
from jwt.exceptions import InvalidTokenError
from app.core.config import settings
from pydantic import ValidationError

# newline
oauth2 = OAuth2PasswordBearer(
    tokenUrl="api/login/access-token",
    scheme_name="Oauth2",
)

TokenDep = Annotated[str, Depends(oauth2)]

ALGORITHM = "HS256"


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


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
        token_data = TokenPayload(**payload)
    except InvalidTokenError, ValidationError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core import security
from app.core.config import settings
from app.domain.exceptions import PasswordMatchError, UserNotFound
from app.domain.schemas import Token
from app.services.deps import UserServiceDep

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/access-token")
def create_token(
    service: UserServiceDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    try:
        user_id = service.check(form_data.username, form_data.password)
    except (UserNotFound, PasswordMatchError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect name or password",
        )
    token = Token(
        access_token=security.create_token(
            user_id,
            expires_delta=timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES),
        )
    )
    return token

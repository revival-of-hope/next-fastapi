from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.crud import check_db, check_user
from app.api.deps import SessionDep
from app.models import Token
from app.core import security

router = APIRouter(tags=["utils"])

TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8


@router.get("/utils/health")
async def health_check(session: SessionDep) -> bool:
    return check_db(session=session)


@router.post("/login/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = check_user(
        session=session,
        name=form_data.username,
        password=form_data.password,
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect name or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    token_expires = timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_token(
            user.id,
            expires_delta=token_expires,
        )
    )

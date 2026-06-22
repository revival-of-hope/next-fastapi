from collections.abc import Generator
from typing import Annotated

from sqlmodel import Session
from app.core.db import init_db, engine
from fastapi import Depends, HTTPException
from app.models import User


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


def fake_get_current_user(session: SessionDep) -> User:
    user = session.get(User, 114514)
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")
    return user


CurrentUser = Annotated[User, Depends(fake_get_current_user)]

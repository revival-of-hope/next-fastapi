from app.utils.security import (
    verify_password,
    hashing_password,
)
from fastapi import HTTPException
from sqlmodel import Session, select
from app.models import User, UserLogin, UserRegister, ChatMessage


def healthchecker(session: Session):
    result = session.exec(select(1)).one()
    return result == 1


def register_user(session: Session, user_create: UserRegister) -> User:
    user_store = User.model_validate(
        user_create, update={"hashed_password": hashing_password(user_create.password)}
    )
    # 数据库存储
    session.add(user_store)
    session.commit()
    session.refresh(user_store)

    # 返回信息供路由函数处理
    return user_store


def check_user(session: Session, user_login: UserLogin, user_db: User):
    user = session.exec(select(User).where(user_login.name == user_db.name)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(UserLogin.password, User.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return user

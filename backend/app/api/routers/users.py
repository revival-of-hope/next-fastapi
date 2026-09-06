from fastapi import APIRouter, HTTPException
from app.api.deps import SessionDep, CurrentUser
from app.models import User, UserPublic, UserRegister
from app import crud

router = APIRouter(prefix="/users", tags=["users"])


# response_model用于过滤不必要的信息返回
@router.post("", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> User:
    user = crud.get_user_by_name(session=session, name=user_in.name)
    if user:
        # 由于没有邮箱,所以只好用名字来进行唯一标识
        raise HTTPException(status_code=400, detail="Name exists")
    user_register = UserRegister.model_validate(user_in)
    user = crud.register_user(session=session, user_register=user_register)
    return user


# 获取用户个人信息
@router.get("/me", response_model=UserPublic)
def homepage(current_user: CurrentUser) -> User:
    return current_user

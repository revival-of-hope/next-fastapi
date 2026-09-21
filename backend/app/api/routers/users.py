from fastapi import APIRouter, HTTPException, status, Response
from app.api.deps import SessionDep, CurrentUser, Superuser
from app.models import User, UserPublic, UserRegister
from app import crud
from app.models.schemas import UsagePublic, UsersPublic

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
def register_user(session: SessionDep, user_in: UserRegister) -> User:
    user = crud.get_user_by_name(session=session, name=user_in.name)
    if user:
        # 由于没有邮箱,所以只好用名字来进行唯一标识
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Name already exists")
    user = crud.register_user(session=session, user_register=user_in)
    return user


# 获取用户个人信息
@router.get("/me", response_model=UserPublic)
def user_homepage(current_user: CurrentUser) -> User:
    return current_user


# 获取用户列表
@router.get("", response_model=UsersPublic)
def read_users(
    _: Superuser,
    session: SessionDep,
    skip: int,
    limit: int = 100,
) -> UsersPublic:
    return crud.get_users(session=session, offset=skip, limit=limit)


@router.get("/usage", response_model=UsagePublic)
def read_usage(_: Superuser, session: SessionDep):
    return crud.get_usage_totals(session=session)


# 删除用户
@router.delete("/{user_id}")
def delete_user(current_user: Superuser, session: SessionDep, user_id: int) -> Response:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="Super users are not allowed to delete themselves",
        )
    try:
        session.delete(user)
        session.commit()
    except Exception:
        session.rollback()
        raise

    return Response(status_code=status.HTTP_204_NO_CONTENT)

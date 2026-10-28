from fastapi import APIRouter, HTTPException, status
from app.domain.exceptions import UserCreateError, UserDeleteError, UserNotFound
from app.services.deps import UserServiceDep, CurrentUserID, SuperuserID
from app.domain.schemas import UserPublic, UsersPublic, UserRegister
from app.domain.schemas import UsersPublic

router = APIRouter(prefix="/users", tags=["users"])


# 用户注册
@router.post("", status_code=status.HTTP_201_CREATED)
def user_register(serivce: UserServiceDep, user_in: UserRegister) -> UserPublic:
    user = serivce.get_by_name(user_in.name)
    if user:
        # 由于没有邮箱,所以只好用名字来进行唯一标识
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="Name already exists",
        )
    try:
        user = serivce.post(user_in)
    except UserCreateError as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        ) from e

    return user


# 获取用户个人信息
@router.get("/me", status_code=status.HTTP_200_OK)
def get_user(service: UserServiceDep, user_id: CurrentUserID) -> UserPublic:
    try:
        user = service.get_by_id(user_id)
    except UserNotFound as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found") from e
    return user


# 获取用户列表
@router.get("", status_code=status.HTTP_200_OK)
def get_users_list(
    _: SuperuserID,
    service: UserServiceDep,
    skip: int,
    limit: int,
) -> UsersPublic:
    return service.get_all(offset=skip, limit=limit)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(
    service: UserServiceDep, current_user_id: CurrentUserID
) -> None:
    try:
        service.delete(current_user_id)
    except UserDeleteError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User cannot be deleted",
        )
    except UserNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


# 删除用户
@router.delete("/{user_id}")
def superuser_delete_user(
    service: UserServiceDep,
    superuser_id: SuperuserID,
    user_id: int,
) -> None:
    if superuser_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superusers are not allowed to delete themselves",
        )
    try:
        service.delete(user_id)
    except UserDeleteError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User cannot be deleted",
        )
    except UserNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

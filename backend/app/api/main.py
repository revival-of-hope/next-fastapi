from fastapi import APIRouter
from fastapi.routing import APIRoute
from app.api.routers import utils
from app.api.routers import user


def generate_operation_id(route: APIRoute):
    """
    根据路由路径生成 operationId

    /api/user/me
    -> ApiUserMeGet

    /api/user/chat
    -> ApiUserChatPost
    """

    path = route.path_format

    # 去掉开头 /
    parts = [item for item in path.strip("/").split("/") if item]

    name = "".join(
        part.replace("{", "By")
        .replace("}", "")
        .replace("-", "_")
        .split("_")[0]
        .capitalize()
        for part in parts
    )

    # HTTP方法
    method = list(route.methods)[0].lower()

    return name + method.capitalize()


api_router = APIRouter(generate_unique_id_function=generate_operation_id)
api_router.include_router(user.router)
api_router.include_router(utils.router)

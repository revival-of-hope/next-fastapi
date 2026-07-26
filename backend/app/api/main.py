from ctypes import util

from fastapi import APIRouter
from app.api.routers import utils
from app.api.routers import user

api_router = APIRouter()
api_router.include_router(user.router)
api_router.include_router(utils.router)

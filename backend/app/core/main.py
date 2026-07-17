from ctypes import util

from fastapi import APIRouter
from app.core.routers import user, utils

api_router = APIRouter()
api_router.include_router(user.router)
api_router.include_router(utils.router)

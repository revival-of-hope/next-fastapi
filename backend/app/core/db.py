from sqlmodel import (
    create_engine,
    SQLModel,
)
from app import models
from app.utils.config import settings

engine = create_engine(str(settings.DATABASE_URI))


def init_db() -> None:
    SQLModel.metadata.create_all(engine)

from sqlmodel import (
    create_engine,
    SQLModel,
)
from app.models import tables
from app.core.config import settings

engine = create_engine(str(settings.DATABASE_URI))


def init_db() -> None:
    SQLModel.metadata.create_all(engine)

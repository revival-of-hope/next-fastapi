from sqlmodel import create_engine, Session
from app.core.config import settings

from app.domain.schemas import UserCreate

from app.infra.repo import UserRepo

engine = create_engine(
    str(settings.DATABASE_URI),
)


def init_db(session: Session) -> None:
    repo = UserRepo(session)
    userrecord = repo.get_by_name(settings.SUPERUSER_NAME)
    if not userrecord:
        new_user = UserCreate(
            name=settings.SUPERUSER_NAME,
            password=settings.SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        repo.post(new_user)

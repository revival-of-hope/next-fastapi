from sqlmodel import create_engine, Session, select

from app.core.config import settings
from app.models import User, UserCreate
from app import crud

engine = create_engine(
    str(settings.DATABASE_URI),
)


def init_db(session: Session) -> None:
    user = session.exec(
        select(User).where(User.name == settings.SUPERUSER_NAME)
    ).first()
    if not user:
        new_user = UserCreate(
            name=settings.SUPERUSER_NAME,
            password=settings.SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.register_user(session=session, user_register=new_user)

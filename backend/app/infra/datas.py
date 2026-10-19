from sqlmodel import Session, select, func
from app.models import UserRecord

# Dummy hash to use for timing attack prevention when user is not found
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"


def users_amount(session: Session) -> int:
    statement = select(func.count()).select_from(UserRecord)

    amount = session.exec(statement).one()
    return amount

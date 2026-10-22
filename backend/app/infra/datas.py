from sqlmodel import Session, select, func
from app.models import UserRecord
from app.domain.models import MessageRole, TokenUsage, UserUsage
from app.domain.schemas import UsagePublic

# Dummy hash to use for timing attack prevention when user is not found
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"
HISTORY_MESSAGE_LIMIT = 4


def users_amount(session: Session) -> int:
    statement = select(func.count()).select_from(UserRecord)

    amount = session.exec(statement).one()
    return amount


def _add_tokens(userusage: UserUsage, usage: TokenUsage) -> None:
    userusage.input_tokens += usage.input_tokens
    userusage.output_tokens += usage.output_tokens
    userusage.total_tokens += usage.total_tokens


def add_usage(userusage: UserUsage, usage: TokenUsage, role: MessageRole) -> None:
    if role == MessageRole.ASSISTANT:
        _add_tokens(userusage, usage)
    userusage.messages_count += 1


def get_usage_totals(session: Session) -> UsagePublic:
    statement = select(
        func.coalesce(func.sum(UserUsage.messages_count), 0),
        func.coalesce(func.sum(UserUsage.input_tokens), 0),
        func.coalesce(func.sum(UserUsage.output_tokens), 0),
        func.coalesce(func.sum(UserUsage.total_tokens), 0),
    )

    result = session.exec(statement).one()

    return UsagePublic(
        messages_count=int(result[0]),
        input_tokens=int(result[1]),
        output_tokens=int(result[2]),
        total_tokens=int(result[3]),
    )

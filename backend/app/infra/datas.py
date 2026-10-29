from sqlmodel import Session, select, func
from app.models import UserRecord
from app.domain.models import MessageRole, TokenUsage, UserUsage
from app.domain.schemas import UsagePublic
from app.core.config import settings
from app.models.tables import UserUsageRecord

# Dummy hash to use for timing attack prevention when user is not found
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"


def users_amount(session: Session) -> int:
    statement = select(func.count()).select_from(UserRecord)

    amount = session.exec(statement).one()
    return amount


def build_conversation_title(content: str) -> str:

    normalized_text = " ".join(content.split())
    if not normalized_text:
        return settings.DEFAULT_TITLE

    return normalized_text[: settings.TITLE_LENGTH]


def _add_tokens(userusage: UserUsageRecord, usage: TokenUsage) -> None:
    userusage.input_tokens += usage.input_tokens
    userusage.output_tokens += usage.output_tokens
    userusage.total_tokens += usage.total_tokens


def add_usage(userusage: UserUsageRecord, usage: TokenUsage, role: MessageRole) -> None:
    if role == MessageRole.ASSISTANT:
        _add_tokens(userusage, usage)
    userusage.messages_count += 2


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

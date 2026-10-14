from datetime import UTC, datetime


def get_datetime() -> datetime:
    return datetime.now(UTC)

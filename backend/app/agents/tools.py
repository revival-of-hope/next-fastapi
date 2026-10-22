from functools import lru_cache
from openai import OpenAI
from app.core.config import settings
from app.domain.schemas import MessagesPublic
from openai.types.responses import (
    EasyInputMessageParam,
    ResponseInputParam,
)


def build_client(*, api_key: str, url: str) -> OpenAI:
    return OpenAI(api_key=api_key, base_url=url)


@lru_cache
def default_client() -> OpenAI:
    return build_client(
        api_key=settings.DEEPSEEK_API_KEY,
        url=settings.MODEL_URL,
    )


def build_inputs(history: MessagesPublic) -> ResponseInputParam:
    response_input: ResponseInputParam = []
    for message in history.data:
        response_input.append(
            EasyInputMessageParam(
                role=message.role,  # type: ignore
                content=message.content,
            )
        )
    return response_input


def build_conversation_title(content: str) -> str:

    normalized_text = " ".join(content.split())
    if not normalized_text:
        return settings.DEFAULT_TITLE

    return normalized_text[: settings.TITLE_LENGTH]

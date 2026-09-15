from openai import OpenAI
from app.utils.stream import (
    build_messages,
    stream_response,
    create_stream,
    create_client,
)
from functools import lru_cache

from app.models import Message
from app.core.config import settings
from collections.abc import Iterator

DEFAULT_MODEL = "deepseek-v4-pro"
DEFAULT_SYSTEM_PROMPT = "以后的回答都要优先输出一句话,我是deepseek-v4-pro."


@lru_cache
def get_client() -> OpenAI:
    return create_client(
        api_key=settings.DEEPSEEK_API_KEY,
        url=settings.DEEPSEEK_URL,
    )


def stream_agent(
    *,
    history: list[Message],
    model: str = DEFAULT_MODEL,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
) -> Iterator[str]:
    # 构造消息列表
    message_list = build_messages(system_prompt=system_prompt, history=history)

    # 打开通信流
    stream = create_stream(
        client=get_client(),
        model=model,
        messages=message_list,
    )
    return stream_response(stream)

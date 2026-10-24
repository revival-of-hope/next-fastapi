from functools import lru_cache
from openai import OpenAI, Stream
from openai.types.responses import ResponseStreamEvent
from app.core.config import settings
from app.agents.streams import build_client, build_inputs, create_stream

from app.domain.schemas import MessagesPublic


@lru_cache
def default_client() -> OpenAI:
    return build_client(
        api_key=settings.DEEPSEEK_API_KEY,
        url=settings.MODEL_URL,
    )


def default_agent(
    history: MessagesPublic,
    content: str,
    model: str = settings.MODEL_NAME,
    system_prompt: str = settings.DEFAULT_SYSTEM_PROMPT,
    reasoning: str = "medium",
) -> Stream[ResponseStreamEvent]:
    input = build_inputs(history, content)

    stream = create_stream(
        client=default_client(),
        model=model,
        instructions=system_prompt,
        input=input,
        reasoning=reasoning,
    )
    return stream

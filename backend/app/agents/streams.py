from openai import OpenAI, Stream
from openai.types.responses import (
    ResponseInputParam,
    ResponseStreamEvent,
)

from app.domain.schemas import MessagesPublic
from app.core.config import settings
from app.agents.tools import build_inputs, default_client


def create_stream(
    self,
    *,
    client: OpenAI,
    model: str,
    instructions: str,
    input: ResponseInputParam,
    reasoning: str = "none",
) -> Stream[ResponseStreamEvent]:

    return client.responses.create(
        model=model,
        instructions=instructions,
        input=input,
        stream=True,
        reasoning=({"effort": reasoning}),  # type: ignore
    )


def default_agent(
    self,
    *,
    history: MessagesPublic,
    model: str = settings.MODEL_NAME,
    system_prompt: str = settings.DEFAULT_SYSTEM_PROMPT,
    reasoning: str = "medium",
) -> Stream[ResponseStreamEvent]:
    input = build_inputs(history)

    stream = self.create_stream(
        client=default_client(),
        model=model,
        instructions=system_prompt,
        input=input,
        reasoning=reasoning,
    )
    return stream

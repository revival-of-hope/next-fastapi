from typing import Iterator, Sequence
from openai import Stream, OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionChunk,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from app.models import Message, MessageRole


# history代表历史消息
def build_messages(
    *,
    system_prompt: str,
    history: list[Message],
) -> list[ChatCompletionMessageParam]:
    messages: list[ChatCompletionMessageParam] = [
        ChatCompletionSystemMessageParam(role="system", content=system_prompt)
    ]
    for message in history:
        if message.role is MessageRole.USER:
            messages.append(
                ChatCompletionUserMessageParam(
                    role="user",
                    content=message.content,
                )
            )
        else:
            messages.append(
                ChatCompletionAssistantMessageParam(
                    role="assistant",
                    content=message.content,
                )
            )
    return messages


def create_client(*, api_key: str, url: str) -> OpenAI:
    return OpenAI(api_key=api_key, base_url=url)


def create_stream(
    *,
    client: OpenAI,
    model: str,
    messages: list[ChatCompletionMessageParam],
) -> Stream[ChatCompletionChunk]:
    return client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        reasoning_effort="medium",
        stream_options={
            "include_usage": True,
        },
    )

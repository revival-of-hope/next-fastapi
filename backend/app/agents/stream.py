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
    )


def stream_response(
    stream: Stream[ChatCompletionChunk],
) -> Iterator[str]:
    for chunk in stream:
        # 某些 chunk 可能没有 choices
        if not chunk.choices:
            continue

        # delta 表示“这一次新增的内容”。
        delta = chunk.choices[0].delta

        # delta.content 可能是 None。
        if delta.content:
            yield delta.content

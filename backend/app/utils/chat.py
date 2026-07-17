from typing import Generator
from openai import Stream, OpenAI
from openai.types.chat import ChatCompletionChunk

from app.crud import save_chat_message


def messages(user_message: str, system_prompt: str) -> list[dict]:
    return [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_message,
        },
    ]


def create_client(api_key: str, url: str):
    return OpenAI(api_key=api_key, base_url=url)


def stream_response(
    stream: Stream[ChatCompletionChunk],
) -> Generator[str, None, None]:
    for chunk in stream:
        # 某些 chunk 可能没有 choices
        if not chunk.choices:
            continue

        # delta 表示“这一次新增的内容”。
        delta = chunk.choices[0].delta

        # delta.content 可能是 None。
        if delta.content:
            yield delta.content


def create_stream(
    client,
    model: str,
    user_message: str,
    system_prompt: str,
):
    stream = client.chat.completions.create(
        model=model,
        messages=messages(user_message, system_prompt),
        stream=True,
        reasoning_effort="high",
    )
    return stream

from typing import Generator
from openai import Stream, OpenAI
from openai.types.chat import ChatCompletionChunk
from sqlmodel import Session

from app.crud import save_message
from app.models import Conversation, MessageRole


# history代表历史消息
def messages(user_message: str, system_prompt: str, history) -> list[dict]:
    return [
        {
            "role": "system",
            "content": system_prompt,
        },
        history,
        {
            "role": "user",
            "content": user_message,
        },
    ]


def create_client(api_key: str, url: str):
    return OpenAI(api_key=api_key, base_url=url)


def create_stream(
    client: OpenAI,
    model: str,
    messages,
):
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        reasoning_effort="medium",
    )
    return stream


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


def stream_and_save(*, session: Session, conversation: Conversation, chunks):
    collected_chunks: list[str] = []

    for chunk in chunks:
        if not chunk:
            continue

        collected_chunks.append(chunk)
        yield chunk

    full_content = "".join(collected_chunks)

    if full_content:
        save_message(
            role=MessageRole.ASSISTANT,
            conversation=conversation,
            content=full_content,
            session=session,
        )

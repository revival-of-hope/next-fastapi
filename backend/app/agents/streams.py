from typing import Generator

from openai import OpenAI, Stream
from openai.types.responses import (
    ResponseInputParam,
    ResponseStreamEvent,
    Response,
    EasyInputMessageParam,
)

from app.domain.models import MessageRole
from app.domain.schemas import MessagesPublic, ResponsePublic
from app.domain.models import TokenUsage


def _build_history(history: MessagesPublic) -> ResponseInputParam:
    history_list: ResponseInputParam = []
    for message in history.data:
        history_list.append(
            EasyInputMessageParam(
                role=message.role,  # type: ignore
                content=message.content,
            )
        )
    return history_list


def build_inputs(history: MessagesPublic, content: str) -> ResponseInputParam:
    history_list = _build_history(history)
    inputs: ResponseInputParam = history_list
    inputs.append(
        EasyInputMessageParam(
            role=MessageRole.USER,  # type: ignore
            content=content,
        )
    )
    return inputs


def build_client(*, api_key: str, url: str) -> OpenAI:
    return OpenAI(api_key=api_key, base_url=url)


def create_stream(
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


def _stream_output(
    stream: Stream[ResponseStreamEvent],
) -> Generator[dict[str, str], None, Response]:
    final_response: Response | None = None
    for event in stream:
        # thinking字段和answer字段
        if event.type == "response.reasoning_text.delta":
            yield {"type": "reasoning", "content": event.delta}
        elif event.type == "response.output_text.delta":
            yield {"type": "answer", "content": event.delta}

        # 错误处理
        elif event.type == "error":
            raise RuntimeError(event.message)
        elif event.type == "response.failed":
            error = event.response.error
            if error:
                raise RuntimeError(error.message)
            else:
                raise RuntimeError("Response failed")

        # 完成输出
        elif event.type == "response.completed" or event.type == "response.incomplete":
            final_response = event.response

    if not final_response:
        raise Exception

    return final_response


def standard_stream(
    stream: Stream[ResponseStreamEvent],
) -> Generator[dict[str, str], None, ResponsePublic]:
    try:
        raw_response = yield from _stream_output(stream)
    except:
        raise
    usage = raw_response.usage
    if usage is None:
        raise

    tokenusage = TokenUsage(
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        total_tokens=usage.total_tokens,
    )
    response = ResponsePublic(
        output_text=raw_response.output_text,
        usage=tokenusage,
    )
    return response

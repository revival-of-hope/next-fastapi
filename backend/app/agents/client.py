from functools import lru_cache
from typing import Literal

from app.models import Message, MessageRole
from app.core.config import settings

from openai import Stream, OpenAI
from openai.types.responses import (
    EasyInputMessageParam,
    ResponseInputParam,
    ResponseStreamEvent,
)


class Agent:
    DEFAULT_MODEL = "deepseek-v4-pro"
    DEFAULT_SYSTEM_PROMPT = "以后的回答都要优先输出一句话,我是deepseek-v4-pro."

    @lru_cache
    def _get_client(self) -> OpenAI:
        return self._create_client(
            api_key=settings.DEEPSEEK_API_KEY,
            url=settings.DEEPSEEK_URL,
        )

    def stream_agent(
        self,
        *,
        history: list[Message],
        model: str = DEFAULT_MODEL,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ) -> Stream[ResponseStreamEvent]:
        # 构造消息列表
        message_list = self._build_input(history=history)

        # 打开通信流
        stream = self._create_stream(
            client=self._get_client(),
            model=model,
            instructions=system_prompt,
            input=message_list,
        )
        return stream

    @staticmethod
    def _build_input(
        *,
        history: list[Message],
    ) -> ResponseInputParam:
        response_input: ResponseInputParam = []
        for message in history:
            role: Literal["user", "assistant"] = (
                "user" if message.role is MessageRole.USER else "assistant"
            )
            response_input.append(
                EasyInputMessageParam(
                    role=role,
                    content=message.content,
                )
            )
        return response_input

    @staticmethod
    def _create_client(*, api_key: str, url: str) -> OpenAI:
        return OpenAI(api_key=api_key, base_url=url)

    @staticmethod
    def _create_stream(
        *,
        client: OpenAI,
        model: str,
        instructions: str,
        input: ResponseInputParam,
    ) -> Stream[ResponseStreamEvent]:
        return client.responses.create(
            model=model,
            instructions=instructions,
            input=input,
            stream=True,
            reasoning={"effort": "high"},
        )

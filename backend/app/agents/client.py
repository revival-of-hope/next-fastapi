from functools import lru_cache

from app.models import Message, MessageRole
from app.core.config import settings

from openai import Stream, OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionChunk,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
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
    ) -> Stream[ChatCompletionChunk]:
        # 构造消息列表
        message_list = self._build_messages(
            system_prompt=system_prompt, history=history
        )

        # 打开通信流
        stream = self._create_stream(
            client=self._get_client(),
            model=model,
            messages=message_list,
        )
        return stream
        # history代表历史消息

    @staticmethod
    def _build_messages(
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

    @staticmethod
    def _create_client(*, api_key: str, url: str) -> OpenAI:
        return OpenAI(api_key=api_key, base_url=url)

    @staticmethod
    def _create_stream(
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

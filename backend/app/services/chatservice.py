from typing import Generator

from app.agents.streams import standard_stream
from app.domain.models import MessageRole, TokenUsage
from app.services.baseservice import BaseService
from app.infra.repo import ConversationRepo
from app.domain.schemas import (
    ConversationPublic,
    ConversationsPublic,
    MessagesPublic,
    UsagePublic,
)
from app.core.config import settings
from app.agents.preset import default_agent
from app.agents.streams import build_inputs


class ChatService(BaseService[ConversationRepo]):
    def get_messages(self, conversation_id: int, user_id: int) -> MessagesPublic:
        messages = self._repo.get_messages(
            conversation_id, user_id, 0, settings.MESSAGE_LIMIT
        )

        return messages

    def get_conversations(
        self, user_id: int, offset: int, limit: int
    ) -> ConversationsPublic:
        try:
            conversations = self._repo.get_all(user_id, offset, limit)
        except:
            raise Exception
        return conversations

    def post_conversation(self, user_id: int, content: str) -> ConversationPublic:
        conversation = self._repo.post(user_id, content)
        if not conversation:
            raise Exception
        return conversation

    def update_conversation_title(self, conversation_id: int, title: str) -> None:
        try:
            self._repo.update_title(conversation_id, title)
        except:
            raise Exception

    def post_message(
        self, conversation_id: int, content: str, role: MessageRole
    ) -> None:
        self._repo.post_message(conversation_id, role, content)

    def post_usage(
        self, user_id: int, tokenusage: TokenUsage, role: MessageRole
    ) -> None:
        self._repo.post_usage(user_id, tokenusage, role)

    def get_usages(self) -> UsagePublic:
        return self._repo.get_usages()

    def stream_and_save(
        self,
        user_id: int,
        conversation_id: int,
        content: str,
        reasoning: str,
    ) -> Generator[dict[str, str], None, None]:

        # 权限验证
        try:
            self._repo.get(conversation_id, user_id)
        except:
            raise
        # 获取历史消息
        history_message = self._repo.get_messages(conversation_id, user_id)

        # 创建默认Agent和流
        client = default_agent(
            history=history_message,
            content=content,
            reasoning=reasoning,
        )
        response = yield from standard_stream(client)

        # 存储消息
        try:
            self._repo.post_usage(user_id, response.usage, MessageRole.ASSISTANT)
            self._repo.post_message(conversation_id, MessageRole.USER, content)
            self._repo.post_message(
                conversation_id, MessageRole.ASSISTANT, response.output_text
            )
        except:
            raise

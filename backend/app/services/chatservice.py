from typing import Generator

from app.agents.streams import standard_stream
from app.domain.exceptions import (
    ChatSaveError,
    ConversationCreateError,
    ConversationNotFound,
    ConversationRecordCreateError,
    ConversationRecordNotFound,
    ConversationTitleUpdateError,
    MessageCreateError,
    MessageRecordCreateError,
    MessageRecordNotFound,
    MessagesNotFound,
    TitleUpdateError,
    UsageUpdateError,
    UsagesNotFound,
)
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


class ChatService(BaseService[ConversationRepo]):
    def get_messages(self, conversation_id: int, user_id: int) -> MessagesPublic:
        try:
            messages = self._repo.get_messages(
                conversation_id, user_id, 0, settings.MESSAGE_LIMIT
            )
        except MessageRecordNotFound:
            raise MessagesNotFound("Messages not found")
        return messages

    def get_conversations(
        self, user_id: int, offset: int, limit: int
    ) -> ConversationsPublic:
        try:
            conversations = self._repo.get_all(user_id, offset, limit)
        except ConversationRecordNotFound:
            raise ConversationNotFound("Conversation not found")
        return conversations

    def post_conversation(self, user_id: int, content: str) -> ConversationPublic:
        try:
            conversation = self._repo.post(user_id, content)
        except ConversationRecordCreateError:
            raise ConversationCreateError("Fail to create conversation")
        return conversation

    def update_conversation_title(
        self, user_id: int, conversation_id: int, title: str
    ) -> None:
        try:
            self._repo.update_title(user_id, conversation_id, title)
        except ConversationTitleUpdateError:
            raise TitleUpdateError("Fail to update conversation title")
        except ConversationRecordNotFound:
            raise ConversationNotFound("Conversation not found")

    def post_message(
        self, conversation_id: int, content: str, role: MessageRole
    ) -> None:
        try:
            self._repo.post_message(conversation_id, role, content)
        except MessageRecordCreateError:
            raise MessageCreateError("Fail to create message")

    def post_usage(
        self, user_id: int, tokenusage: TokenUsage, role: MessageRole
    ) -> None:
        try:
            self._repo.post_usage(user_id, tokenusage, role)
        except:
            raise UsageUpdateError("Fail to update usage")

    def get_usages(self) -> UsagePublic:
        try:
            usages = self._repo.get_usages()
        except:
            raise UsagesNotFound("Usages not found")
        return usages

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
        except ConversationRecordNotFound:
            raise ConversationNotFound("Conversation not found")
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
            raise ChatSaveError("Fail to save chat")

from app.services.baseservice import BaseService
from app.infra.repo import ConversationRepo
from app.domain.schemas import MessagesPublic
from app.core.config import settings

class ChatService(BaseService[ConversationRepo]):
    def get_messages(self, conversation_id: int, user_id: int) -> MessagesPublic:
        messages = self._repo.get_messages(conversation_id, user_id,0,MESSAGE_LIMIT)
        return messages
    def post_message(self)

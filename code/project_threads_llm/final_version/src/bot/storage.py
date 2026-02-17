from enum import StrEnum

import structlog
from pydantic import Field, BaseModel
from structlog.typing import FilteringBoundLogger

logger: FilteringBoundLogger = structlog.get_logger()


class Role(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    role: Role
    content: str

    def to_call_dict(self):
        return {
            "role": self.role.value,
            "content": self.content,
        }

    @classmethod
    def from_call_dict(
            cls,
            data: dict[str, str],
    ) -> "Message":
        return cls(
            role=Role(data["role"]),
            content=data["content"],
        )


class LLMChatMeta(BaseModel):
    user_id: int
    thread_id: int  # message_thread_id в терминах Telegram
    prompt_key: str = "default"
    temperature: float = 0.7


class LLMChat(BaseModel):
    meta: LLMChatMeta
    # Системное сообщение НЕ храним в списке messages,
    # оно динамически подставляется из persona_key при запросе к LLM.
    messages: list[Message] = Field(default_factory=list)

    @property
    def is_chat_start(self):
        return len(self.messages) <= 2


class InMemoryChatStorage:
    def __init__(self):
        self.__storage: dict[str, LLMChat] = dict()

    @staticmethod
    def _get_key(
            user_id: int,
            thread_id: int,
    ) -> str:
        return f"{user_id}_{thread_id}"

    async def create(
        self,
        user_id: int,
        thread_id: int,
    ) -> None:
        new_chat_key = self._get_key(user_id, thread_id)
        self.__storage[new_chat_key] = LLMChat(
            meta=LLMChatMeta(
                user_id=user_id,
                thread_id=thread_id,
            )
        )

    async def get(
            self,
            user_id: int,
            thread_id: int,
    ) -> LLMChat | None:
        return self.__storage.get(self._get_key(user_id, thread_id))

    async def update(
            self,
            user_id: int,
            thread_id: int,
            new_version: LLMChat,
    ):
        llm_chat_id = self._get_key(user_id, thread_id)
        self.__storage[llm_chat_id] = new_version


memory_chat_storage = InMemoryChatStorage()

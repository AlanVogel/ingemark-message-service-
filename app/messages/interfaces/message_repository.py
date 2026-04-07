from typing import Protocol
from uuid import UUID

from app.messages.dto import CreateMessageDto, UpdateMessageDto
from app.messages.model import Message


class IMessageRepository(Protocol):
    """Interface for message repository.

    Using Python's Protocol for structural typing — any class
    that implements these methods satisfies the interface,
    no explicit inheritance needed.
    """

    async def create(self, dto: CreateMessageDto) -> Message: ...

    async def update(self, message_id: UUID, dto: UpdateMessageDto) -> Message | None: ...

    async def get_all(
        self,
        chat_id: UUID | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Message], int]: ...

    async def get_by_id(self, message_id: UUID) -> Message | None: ...

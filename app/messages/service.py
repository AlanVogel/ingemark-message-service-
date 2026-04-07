import math
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.core.exceptions import IngemarkConflictError, IngemarkNotFoundError
from app.messages.dto import CreateMessageDto, UpdateMessageDto
from app.messages.interfaces.message_repository import IMessageRepository
from app.messages.responses import MessageResponse, PaginatedMessagesResponse


class MessageService:
    """Business logic layer for messages.

    Sits between router and repository.
    Handles validation, error mapping, and response formatting.
    Depends on IMessageRepository protocol — not the concrete implementation.
    """

    def __init__(self, repository: IMessageRepository):
        self._repository = repository

    async def create_message(self, dto: CreateMessageDto) -> MessageResponse:
        try:
            message = await self._repository.create(dto)
        except IntegrityError:
            raise IngemarkConflictError(f"Message with id '{dto.message_id}' already exists")
        return MessageResponse.model_validate(message)

    async def update_message(self, message_id: UUID, dto: UpdateMessageDto) -> MessageResponse:
        message = await self._repository.update(message_id, dto)
        if not message:
            raise IngemarkNotFoundError(f"Message with id '{message_id}' not found")
        return MessageResponse.model_validate(message)

    async def get_all_messages(
        self,
        chat_id: UUID | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedMessagesResponse:
        messages, total = await self._repository.get_all(chat_id, page, page_size)
        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return PaginatedMessagesResponse(
            items=[MessageResponse.model_validate(m) for m in messages],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

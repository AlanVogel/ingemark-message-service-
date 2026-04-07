from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.messages.dto import CreateMessageDto, UpdateMessageDto
from app.messages.model import Message


class MessageRepository:
    """PostgreSQL implementation of message repository.

    Single responsibility: database operations only.
    No business logic, no HTTP concerns, no validation.
    """

    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, dto: CreateMessageDto) -> Message:
        message = Message(
            message_id=dto.message_id,
            chat_id=dto.chat_id,
            content=dto.content,
            rating=dto.rating,
            sent_at=dto.sent_at,
            role=dto.role.value,
        )
        self._db.add(message)
        await self._db.flush()
        await self._db.refresh(message)
        return message

    async def update(self, message_id: UUID, dto: UpdateMessageDto) -> Message | None:
        message = await self.get_by_id(message_id)
        if not message:
            return None

        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(message, field, value)

        await self._db.flush()
        await self._db.refresh(message)
        return message

    async def get_all(
        self,
        chat_id: UUID | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Message], int]:
        query = select(Message)

        if chat_id:
            query = query.where(Message.chat_id == chat_id)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self._db.execute(count_query)).scalar() or 0

        paginated = (
            query.order_by(Message.sent_at.desc()).offset((page - 1) * page_size).limit(page_size)
        )
        result = await self._db.execute(paginated)
        messages = list(result.scalars().all())

        return messages, total

    async def get_by_id(self, message_id: UUID) -> Message | None:
        query = select(Message).where(Message.message_id == message_id)
        result = await self._db.execute(query)
        return result.scalars().first()

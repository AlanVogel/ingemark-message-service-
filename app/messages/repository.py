from uuid import UUID

from sqlalchemy.orm import Session

from app.messages.dto import CreateMessageDto, UpdateMessageDto
from app.messages.model import Message


class MessageRepository:
    """PostgreSQL implementation of message repository.

    Single responsibility: database operations only.
    No business logic, no HTTP concerns, no validation.
    """

    def __init__(self, db: Session):
        self._db = db

    def create(self, dto: CreateMessageDto) -> Message:
        message = Message(
            message_id=dto.message_id,
            chat_id=dto.chat_id,
            content=dto.content,
            rating=dto.rating,
            sent_at=dto.sent_at,
            role=dto.role.value,
        )
        self._db.add(message)
        self._db.flush()
        self._db.refresh(message)
        return message

    def update(self, message_id: UUID, dto: UpdateMessageDto) -> Message | None:
        message = self.get_by_id(message_id)
        if not message:
            return None

        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(message, field, value)

        self._db.flush()
        self._db.refresh(message)
        return message

    def get_all(
        self,
        chat_id: UUID | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Message], int]:
        query = self._db.query(Message)

        if chat_id:
            query = query.filter(Message.chat_id == chat_id)

        total = query.count()
        messages = (
            query.order_by(Message.sent_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return messages, total

    def get_by_id(self, message_id: UUID) -> Message | None:
        return self._db.query(Message).filter(Message.message_id == message_id).first()

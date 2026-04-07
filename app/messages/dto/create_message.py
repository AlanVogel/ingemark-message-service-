from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import Field

from app.messages.dto.base import BaseMessageDto


class MessageRole(StrEnum):
    AI = "ai"
    USER = "user"


class CreateMessageDto(BaseMessageDto):
    """DTO for creating a new message.

    message_id is optional — if not provided, the DB generates one.
    Overrides content to be required (non-optional).
    """

    message_id: UUID | None = Field(
        default=None,
        description="Optional UUID for the message. Auto-generated if omitted.",
    )
    chat_id: UUID = Field(
        description="UUID of the chat this message belongs to.",
        json_schema_extra={"example": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"},
    )
    content: str = Field(
        min_length=1,
        max_length=50000,
        description="The message text content.",
        json_schema_extra={"example": "What is the meaning of life?"},
    )
    sent_at: datetime = Field(
        description="Timestamp when the message was originally sent.",
        json_schema_extra={"example": "2026-04-07T12:00:00Z"},
    )
    role: MessageRole = Field(
        description="Who sent the message: 'ai' or 'user'.",
        json_schema_extra={"example": "user"},
    )

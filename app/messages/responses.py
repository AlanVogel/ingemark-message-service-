from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.messages.dto.create_message import MessageRole


class MessageResponse(BaseModel):
    """Response schema for a single message."""

    message_id: UUID = Field(
        description="Unique identifier for the message.",
        json_schema_extra={"example": "f47ac10b-58cc-4372-a567-0e02b2c3d479"},
    )
    chat_id: UUID = Field(
        description="UUID of the chat this message belongs to.",
        json_schema_extra={"example": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"},
    )
    content: str = Field(
        description="The message text content.",
        json_schema_extra={"example": "What is the meaning of life?"},
    )
    rating: bool | None = Field(
        description="User rating of the message. null if not yet rated.",
        json_schema_extra={"example": True},
    )
    sent_at: datetime = Field(
        description="Timestamp when the message was originally sent.",
        json_schema_extra={"example": "2026-04-07T12:00:00Z"},
    )
    role: MessageRole = Field(
        description="Who sent the message: 'ai' or 'user'.",
        json_schema_extra={"example": "user"},
    )
    created_at: datetime = Field(
        description="Timestamp when the message was persisted.",
        json_schema_extra={"example": "2026-04-07T12:00:00Z"},
    )
    updated_at: datetime | None = Field(
        description="Timestamp of the last update. null if never updated.",
        json_schema_extra={"example": "2026-04-07T12:05:00Z"},
    )

    model_config = {"from_attributes": True}


class PaginatedMessagesResponse(BaseModel):
    """Paginated response for listing messages."""

    items: list[MessageResponse] = Field(description="List of messages on this page.")
    total: int = Field(
        description="Total number of messages matching the query.",
        json_schema_extra={"example": 42},
    )
    page: int = Field(
        description="Current page number.",
        json_schema_extra={"example": 1},
    )
    page_size: int = Field(
        description="Number of items per page.",
        json_schema_extra={"example": 20},
    )
    total_pages: int = Field(
        description="Total number of pages.",
        json_schema_extra={"example": 3},
    )

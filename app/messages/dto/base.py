from pydantic import BaseModel, Field


class BaseMessageDto(BaseModel):
    """Base DTO with shared message fields.

    All fields optional here — child DTOs override to make required as needed.
    """

    content: str | None = Field(
        default=None,
        min_length=1,
        max_length=50000,
        description="The message text content.",
        json_schema_extra={"example": "Updated message content"},
    )
    rating: bool | None = Field(
        default=None,
        description="User rating of the message. null if not yet rated.",
        json_schema_extra={"example": True},
    )

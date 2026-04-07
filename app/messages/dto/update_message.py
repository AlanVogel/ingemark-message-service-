from app.messages.dto.base import BaseMessageDto


class UpdateMessageDto(BaseMessageDto):
    """DTO for updating an existing message.

    Inherits all fields as optional from BaseMessageDto — PATCH semantics.
    Only provided fields get updated.
    """

from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_api_key
from app.core.database import get_db
from app.messages.dto import CreateMessageDto, UpdateMessageDto
from app.messages.repository import MessageRepository
from app.messages.responses import MessageResponse, PaginatedMessagesResponse
from app.messages.service import MessageService

router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
    dependencies=[Depends(verify_api_key)],
)


def _get_service(db: AsyncSession = Depends(get_db)) -> MessageService:
    """Dependency injection: DB session → repository → service."""
    repository = MessageRepository(db)
    return MessageService(repository)


@router.post(
    "/",
    response_model=MessageResponse,
    status_code=201,
    summary="Create a new message",
    description="Persist a new message to the database. "
    "If message_id is not provided, a UUID will be auto-generated.",
    responses={
        201: {"description": "Message created successfully."},
        401: {"description": "Invalid or missing API key."},
        422: {"description": "Validation error — invalid payload."},
    },
)
async def create_message(
    dto: CreateMessageDto,
    service: MessageService = Depends(_get_service),
) -> MessageResponse:
    return await service.create_message(dto)


@router.patch(
    "/{message_id}",
    response_model=MessageResponse,
    summary="Update an existing message",
    description="Partially update a persisted message. "
    "Only provided fields are updated (PATCH semantics).",
    responses={
        200: {"description": "Message updated successfully."},
        401: {"description": "Invalid or missing API key."},
        404: {"description": "Message with the given ID not found."},
        422: {"description": "Validation error — invalid payload."},
    },
)
async def update_message(
    message_id: UUID = Path(description="UUID of the message to update."),
    dto: UpdateMessageDto = ...,
    service: MessageService = Depends(_get_service),
) -> MessageResponse:
    return await service.update_message(message_id, dto)


@router.get(
    "/",
    response_model=PaginatedMessagesResponse,
    summary="List all messages",
    description="Return all messages with pagination. Optionally filter by chat_id.",
    responses={
        200: {"description": "Paginated list of messages."},
        401: {"description": "Invalid or missing API key."},
        422: {"description": "Validation error — invalid query parameters."},
    },
)
async def get_messages(
    chat_id: UUID | None = Query(
        default=None,
        description="Filter messages by chat UUID.",
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="Page number (starts at 1).",
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page (max 100).",
    ),
    service: MessageService = Depends(_get_service),
) -> PaginatedMessagesResponse:
    return await service.get_all_messages(chat_id, page, page_size)

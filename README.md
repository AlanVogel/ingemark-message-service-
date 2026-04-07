# Ingemark Message Service

A message persistence service for an AI assistant system. Built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy 2.0**.

The service is responsible for archiving messages exchanged between users and an AI assistant. It exposes a secured REST API for creating, updating, and retrieving messages, with data persisted in a PostgreSQL database.

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose

### Run the application

```bash
# 1. Clone the repository
git clone https://github.com/your-username/ingemark-message-service.git
cd ingemark-message-service

# 2. Copy environment variables
cp .env.example .env

# 3. Start the application (PostgreSQL + API)
docker compose up --build
```

The API is now available at `http://localhost:8000`.

### Explore the API

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs) — interactive API documentation
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc) — alternative API docs
- **Health check**: [http://localhost:8000/health](http://localhost:8000/health)

### Stop the application

```bash
docker compose down        # stop containers
docker compose down -v     # stop and remove database volume (fresh start)
```

## API Endpoints

All endpoints except `/health` require an `X-API-Key` header.

| Method  | Endpoint                    | Description                              |
|---------|-----------------------------|------------------------------------------|
| `GET`   | `/health`                   | Health check — verifies DB connectivity  |
| `POST`  | `/api/v1/messages/`         | Create a new message                     |
| `PATCH` | `/api/v1/messages/{id}`     | Update an existing message (PATCH)       |
| `GET`   | `/api/v1/messages/`         | List all messages (paginated, filterable)|

### Query parameters for `GET /api/v1/messages/`

| Parameter   | Type   | Default | Description                  |
|-------------|--------|---------|------------------------------|
| `chat_id`   | UUID   | —       | Filter messages by chat      |
| `page`      | int    | 1       | Page number                  |
| `page_size` | int    | 20      | Items per page (max 100)     |

### Message schema

```json
{
  "message_id": "UUID4",
  "chat_id": "UUID4",
  "content": "string",
  "rating": "boolean | null",
  "sent_at": "datetime",
  "role": "ai | user"
}
```

### Example usage

```bash
# Create a message
curl -X POST http://localhost:8000/api/v1/messages/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here" \
  -d '{
    "chat_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "content": "What is the meaning of life?",
    "sent_at": "2026-04-07T12:00:00Z",
    "role": "user"
  }'

# Update a message
curl -X PATCH http://localhost:8000/api/v1/messages/<message_id> \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here" \
  -d '{"rating": true}'

# Get all messages (with pagination and filter)
curl http://localhost:8000/api/v1/messages/?chat_id=a1b2c3d4-e5f6-7890-abcd-ef1234567890&page=1&page_size=10 \
  -H "X-API-Key: your-secret-api-key-here"
```

## Architecture

```
app/
├── main.py                        # Application entry point
├── core/                          # App-wide infrastructure
│   ├── config.py                  # Centralized settings (Pydantic Settings)
│   ├── database.py                # SQLAlchemy engine and session management
│   ├── auth.py                    # API key authentication dependency
│   ├── exceptions.py              # Custom exception hierarchy
│   └── exception_handlers.py      # Global FastAPI exception handlers
├── messages/                      # Message feature module
│   ├── dto/                       # Data Transfer Objects
│   │   ├── base.py                # Base DTO (shared fields — DRY)
│   │   ├── create_message.py      # Create DTO (inherits base, adds required fields)
│   │   └── update_message.py      # Update DTO (inherits base — PATCH semantics)
│   ├── interfaces/                # Abstractions
│   │   └── message_repository.py  # Repository Protocol (dependency inversion)
│   ├── model.py                   # SQLAlchemy entity
│   ├── repository.py              # Database queries (single responsibility)
│   ├── service.py                 # Business logic layer
│   ├── router.py                  # HTTP endpoints with OpenAPI metadata
│   └── responses.py               # Response schemas
└── health/                        # Health check module
    └── router.py
```

### Design Patterns

- **Repository pattern** — separates database queries from business logic
- **Dependency Injection** — FastAPI's `Depends()` chain: DB session → repository → service
- **Protocol (interface)** — `IMessageRepository` for dependency inversion
- **DTO pattern with inheritance** — `BaseMessageDto` with shared validation, child DTOs for create/update
- **Custom exception hierarchy** — `IngemarkBaseError` → `IngemarkNotFoundError`, etc.
- **Global exception handlers** — consistent JSON error responses across the API

### Security

- API key authentication via `X-API-Key` header on all message endpoints
- Secrets managed through environment variables (`.env` file, not committed)
- Non-root user in Docker container
- Input validation via Pydantic schemas

## Development

### Local setup

```bash
# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
make dev

# Run tests
make test

# Run linter and format check
make lint

# Auto-fix formatting
make format
```

### Available Makefile commands

| Command        | Description                        |
|----------------|------------------------------------|
| `make dev`     | Install dependencies in venv       |
| `make test`    | Run pytest                         |
| `make lint`    | Run ruff lint + format check       |
| `make format`  | Auto-fix lint + formatting         |
| `make up`      | Start with Docker Compose          |
| `make down`    | Stop Docker Compose                |
| `make logs`    | Tail container logs                |
| `make migrate` | Run Alembic migrations locally     |

### Database migrations

```bash
# Generate a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

Migrations run automatically on container startup via `entrypoint.sh`.

## CI/CD

Three GitHub Actions workflows:

| Workflow          | Trigger              | Steps                           |
|-------------------|----------------------|---------------------------------|
| **test.yml**      | Pull request         | Lint → Test                     |
| **develop.yml**   | Push to `develop`    | Lint → Test → Docker build      |
| **main.yml**      | Push to `main`       | Lint → Test → Docker build + tag|

## Tech Choices

| Technology             | Reason                                                                      |
|------------------------|-----------------------------------------------------------------------------|
| **FastAPI**            | Async support, auto OpenAPI docs, built-in DI, Pydantic validation          |
| **SQLAlchemy 2.0**     | Mature ORM with type hints, Alembic migration support                       |
| **Alembic**            | Industry standard for SQLAlchemy database migrations                        |
| **Pydantic Settings**  | Type-safe environment variable parsing with validation                      |
| **PostgreSQL**         | Required by assignment; ENUM type for role, UUID for IDs                    |
| **Ruff**               | Fast linter + formatter (replaces flake8, black, isort)                     |
| **pytest**             | Standard Python testing framework with fixtures                             |
| **API key auth**       | Simple, appropriate for service-to-service communication in a larger system |
| **pyproject.toml**     | Modern Python packaging standard (PEP 621) — single config file            |

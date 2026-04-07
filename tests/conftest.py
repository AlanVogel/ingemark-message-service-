import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.core.auth import verify_api_key
from app.core.database import Base, get_db
from app.main import app

TEST_API_KEY = "test-api-key"

postgres = PostgresContainer("postgres:16-alpine", driver="asyncpg")


@pytest.fixture(scope="session", autouse=True)
def postgres_container():
    """Start a real PostgreSQL container for the entire test session."""
    postgres.start()
    yield postgres
    postgres.stop()


@pytest.fixture(autouse=True)
async def setup_db(postgres_container):
    """Create tables before each test, drop after."""
    url = postgres_container.get_connection_url()
    engine = create_async_engine(url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    test_session = async_sessionmaker(bind=engine, expire_on_commit=False)

    async def override_get_db():
        session = test_session()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()
    app.dependency_overrides.pop(get_db, None)


async def override_verify_api_key():
    return TEST_API_KEY


@pytest.fixture
async def client() -> AsyncClient:
    """Async test client with overridden dependencies."""
    app.dependency_overrides[verify_api_key] = override_verify_api_key
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.pop(verify_api_key, None)


@pytest.fixture
async def unauthenticated_client() -> AsyncClient:
    """Async test client with only DB override — no auth bypass."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture
def api_headers() -> dict:
    """Headers with API key for authenticated requests."""
    return {"X-API-Key": TEST_API_KEY}


@pytest.fixture
def sample_message() -> dict:
    """Sample message payload for tests."""
    return {
        "chat_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "content": "What is the meaning of life?",
        "rating": None,
        "sent_at": "2026-03-31T12:00:00Z",
        "role": "user",
    }


@pytest.fixture
def sample_ai_message() -> dict:
    """Sample AI response message."""
    return {
        "chat_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "content": "The meaning of life is 42.",
        "rating": True,
        "sent_at": "2026-03-31T12:00:01Z",
        "role": "ai",
    }

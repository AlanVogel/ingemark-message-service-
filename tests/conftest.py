import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from app.core.auth import verify_api_key
from app.core.database import Base, get_db
from app.main import app

# In-memory SQLite for fast tests (no Docker needed for test DB)
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)

TEST_API_KEY = "test-api-key"


def override_get_db():
    db = TestSession()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def override_verify_api_key():
    return TEST_API_KEY


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test, drop after."""
    # SQLite doesn't support Postgres ENUM, so we need to handle this
    # For full integration tests, use docker-compose.test.yml with real Postgres
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> TestClient:
    """Test client with overridden dependencies."""
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[verify_api_key] = override_verify_api_key
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def unauthenticated_client() -> TestClient:
    """Test client with only DB override — no auth bypass."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


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

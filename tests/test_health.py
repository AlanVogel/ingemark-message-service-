import pytest
from httpx import AsyncClient


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_returns_healthy(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

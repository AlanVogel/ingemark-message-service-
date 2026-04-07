import pytest
from httpx import AsyncClient


class TestGetMessages:
    @pytest.mark.asyncio
    async def test_get_messages_empty(self, client: AsyncClient, api_headers: dict):
        response = await client.get("/api/v1/messages/", headers=api_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_get_messages_returns_created(
        self,
        client: AsyncClient,
        api_headers: dict,
        sample_message: dict,
        sample_ai_message: dict,
    ):
        await client.post("/api/v1/messages/", json=sample_message, headers=api_headers)
        await client.post("/api/v1/messages/", json=sample_ai_message, headers=api_headers)

        response = await client.get("/api/v1/messages/", headers=api_headers)
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    @pytest.mark.asyncio
    async def test_get_messages_filter_by_chat_id(
        self, client: AsyncClient, api_headers: dict, sample_message: dict
    ):
        await client.post("/api/v1/messages/", json=sample_message, headers=api_headers)

        other_msg = sample_message.copy()
        other_msg["chat_id"] = "b2c3d4e5-f6a7-8901-bcde-f12345678901"
        await client.post("/api/v1/messages/", json=other_msg, headers=api_headers)

        response = await client.get(
            f"/api/v1/messages/?chat_id={sample_message['chat_id']}",
            headers=api_headers,
        )
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["chat_id"] == sample_message["chat_id"]

    @pytest.mark.asyncio
    async def test_get_messages_pagination(
        self, client: AsyncClient, api_headers: dict, sample_message: dict
    ):
        for i in range(5):
            msg = sample_message.copy()
            msg["content"] = f"Message {i}"
            await client.post("/api/v1/messages/", json=msg, headers=api_headers)

        response = await client.get("/api/v1/messages/?page=1&page_size=2", headers=api_headers)
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["total_pages"] == 3
        assert data["page"] == 1

    @pytest.mark.asyncio
    async def test_get_messages_without_api_key_returns_401(
        self, unauthenticated_client: AsyncClient
    ):
        response = await unauthenticated_client.get("/api/v1/messages/")
        assert response.status_code == 401

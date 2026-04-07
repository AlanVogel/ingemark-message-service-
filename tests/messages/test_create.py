import pytest
from httpx import AsyncClient


class TestCreateMessage:
    @pytest.mark.asyncio
    async def test_create_message_success(
        self, client: AsyncClient, api_headers: dict, sample_message: dict
    ):
        response = await client.post("/api/v1/messages/", json=sample_message, headers=api_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == sample_message["content"]
        assert data["role"] == sample_message["role"]
        assert data["chat_id"] == sample_message["chat_id"]
        assert "message_id" in data
        assert "created_at" in data
        assert data["updated_at"] is None

    @pytest.mark.asyncio
    async def test_create_message_without_api_key_returns_401(
        self, unauthenticated_client: AsyncClient, sample_message: dict
    ):
        response = await unauthenticated_client.post("/api/v1/messages/", json=sample_message)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_message_empty_content_returns_422(
        self, client: AsyncClient, api_headers: dict
    ):
        payload = {
            "chat_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "content": "",
            "sent_at": "2026-03-31T12:00:00Z",
            "role": "user",
        }
        response = await client.post("/api/v1/messages/", json=payload, headers=api_headers)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_message_invalid_role_returns_422(
        self, client: AsyncClient, api_headers: dict
    ):
        payload = {
            "chat_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "content": "Hello",
            "sent_at": "2026-03-31T12:00:00Z",
            "role": "admin",
        }
        response = await client.post("/api/v1/messages/", json=payload, headers=api_headers)
        assert response.status_code == 422

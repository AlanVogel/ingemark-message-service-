import pytest
from httpx import AsyncClient


class TestUpdateMessage:
    @pytest.mark.asyncio
    async def test_update_message_content(
        self, client: AsyncClient, api_headers: dict, sample_message: dict
    ):
        create_resp = await client.post(
            "/api/v1/messages/", json=sample_message, headers=api_headers
        )
        message_id = create_resp.json()["message_id"]

        update_resp = await client.patch(
            f"/api/v1/messages/{message_id}",
            json={"content": "Updated content"},
            headers=api_headers,
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["content"] == "Updated content"

    @pytest.mark.asyncio
    async def test_update_message_rating(
        self, client: AsyncClient, api_headers: dict, sample_message: dict
    ):
        create_resp = await client.post(
            "/api/v1/messages/", json=sample_message, headers=api_headers
        )
        message_id = create_resp.json()["message_id"]

        update_resp = await client.patch(
            f"/api/v1/messages/{message_id}",
            json={"rating": True},
            headers=api_headers,
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["rating"] is True

    @pytest.mark.asyncio
    async def test_update_nonexistent_message_returns_404(
        self, client: AsyncClient, api_headers: dict
    ):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.patch(
            f"/api/v1/messages/{fake_id}",
            json={"content": "nope"},
            headers=api_headers,
        )
        assert response.status_code == 404

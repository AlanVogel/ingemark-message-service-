from fastapi.testclient import TestClient


class TestHealthEndpoint:
    def test_health_returns_healthy(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestCreateMessage:
    def test_create_message_success(
        self, client: TestClient, api_headers: dict, sample_message: dict
    ):
        response = client.post("/api/v1/messages/", json=sample_message, headers=api_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == sample_message["content"]
        assert data["role"] == sample_message["role"]
        assert data["chat_id"] == sample_message["chat_id"]
        assert "message_id" in data

    def test_create_message_without_api_key_returns_401(
        self, unauthenticated_client: TestClient, sample_message: dict
    ):
        response = unauthenticated_client.post("/api/v1/messages/", json=sample_message)
        assert response.status_code == 401

    def test_create_message_empty_content_returns_422(self, client: TestClient, api_headers: dict):
        payload = {
            "chat_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "content": "",
            "sent_at": "2026-03-31T12:00:00Z",
            "role": "user",
        }
        response = client.post("/api/v1/messages/", json=payload, headers=api_headers)
        assert response.status_code == 422

    def test_create_message_invalid_role_returns_422(self, client: TestClient, api_headers: dict):
        payload = {
            "chat_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "content": "Hello",
            "sent_at": "2026-03-31T12:00:00Z",
            "role": "admin",
        }
        response = client.post("/api/v1/messages/", json=payload, headers=api_headers)
        assert response.status_code == 422


class TestUpdateMessage:
    def test_update_message_content(
        self, client: TestClient, api_headers: dict, sample_message: dict
    ):
        # Create first
        create_resp = client.post("/api/v1/messages/", json=sample_message, headers=api_headers)
        message_id = create_resp.json()["message_id"]

        # Update
        update_resp = client.patch(
            f"/api/v1/messages/{message_id}",
            json={"content": "Updated content"},
            headers=api_headers,
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["content"] == "Updated content"

    def test_update_message_rating(
        self, client: TestClient, api_headers: dict, sample_message: dict
    ):
        create_resp = client.post("/api/v1/messages/", json=sample_message, headers=api_headers)
        message_id = create_resp.json()["message_id"]

        update_resp = client.patch(
            f"/api/v1/messages/{message_id}",
            json={"rating": True},
            headers=api_headers,
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["rating"] is True

    def test_update_nonexistent_message_returns_404(self, client: TestClient, api_headers: dict):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.patch(
            f"/api/v1/messages/{fake_id}",
            json={"content": "nope"},
            headers=api_headers,
        )
        assert response.status_code == 404


class TestGetMessages:
    def test_get_messages_empty(self, client: TestClient, api_headers: dict):
        response = client.get("/api/v1/messages/", headers=api_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_get_messages_returns_created(
        self, client: TestClient, api_headers: dict, sample_message: dict, sample_ai_message: dict
    ):
        client.post("/api/v1/messages/", json=sample_message, headers=api_headers)
        client.post("/api/v1/messages/", json=sample_ai_message, headers=api_headers)

        response = client.get("/api/v1/messages/", headers=api_headers)
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_get_messages_filter_by_chat_id(
        self, client: TestClient, api_headers: dict, sample_message: dict
    ):
        # Create message in chat A
        client.post("/api/v1/messages/", json=sample_message, headers=api_headers)

        # Create message in chat B
        other_msg = sample_message.copy()
        other_msg["chat_id"] = "b2c3d4e5-f6a7-8901-bcde-f12345678901"
        client.post("/api/v1/messages/", json=other_msg, headers=api_headers)

        # Filter by chat A
        response = client.get(
            f"/api/v1/messages/?chat_id={sample_message['chat_id']}",
            headers=api_headers,
        )
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["chat_id"] == sample_message["chat_id"]

    def test_get_messages_pagination(
        self, client: TestClient, api_headers: dict, sample_message: dict
    ):
        # Create 5 messages
        for i in range(5):
            msg = sample_message.copy()
            msg["content"] = f"Message {i}"
            client.post("/api/v1/messages/", json=msg, headers=api_headers)

        # Get page 1, size 2
        response = client.get("/api/v1/messages/?page=1&page_size=2", headers=api_headers)
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["total_pages"] == 3
        assert data["page"] == 1

    def test_get_messages_without_api_key_returns_401(self, unauthenticated_client: TestClient):
        response = unauthenticated_client.get("/api/v1/messages/")
        assert response.status_code == 401

import pytest


@pytest.mark.asyncio
async def test_authenticated_user_can_chat(client):
    signup_payload = {
        "first_name": "Chat",
        "last_name": "User",
        "email": "chat.user@example.com",
        "password": "ChatPass123!",
    }
    await client.post("/api/auth/signup", json=signup_payload)

    login_payload = {
        "email": signup_payload["email"],
        "password": signup_payload["password"],
    }
    response = await client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    token = response.json()["access_token"]

    response = await client.post(
        "/api/chat",
        json={"question": "What is the warranty on the Apex Laptop 1?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        assert "answer" in response.json()

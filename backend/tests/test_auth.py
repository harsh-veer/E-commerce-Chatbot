import pytest

from app.routes.auth import create_access_token
from app.schemas.user import UserCreate


@pytest.mark.asyncio
async def test_signup_and_login(client):
    signup_payload = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test.user@example.com",
        "password": "TestPass123!",
    }

    response = await client.post("/api/auth/signup", json=signup_payload)
    assert response.status_code == 200
    assert response.json()["email"] == signup_payload["email"]

    login_payload = {
        "email": signup_payload["email"],
        "password": signup_payload["password"],
    }
    response = await client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    assert "access_token" in response.json()

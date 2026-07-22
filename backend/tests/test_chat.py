import pytest


@pytest.mark.asyncio
async def test_chat_returns_message_for_unknown_product(client):
    response = await client.post("/api/chat", json={"question": "Do you have a smartphone with 8GB RAM?"})
    assert response.status_code == 401

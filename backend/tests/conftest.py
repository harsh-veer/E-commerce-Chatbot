import asyncio

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database.client import db


pytest_plugins = "pytest_asyncio"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
async def cleanup_db():
    await db.users.delete_many({})
    await db.products.delete_many({})
    await db.chats.delete_many({})
    yield
    await db.users.delete_many({})
    await db.products.delete_many({})
    await db.chats.delete_many({})

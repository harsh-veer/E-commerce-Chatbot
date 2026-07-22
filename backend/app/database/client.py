from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings


client = AsyncIOMotorClient(settings.mongo_uri)
db = client[settings.mongo_db]

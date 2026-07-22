from datetime import datetime

from passlib.context import CryptContext

from app.database.client import db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def seed_admin_user() -> None:
    existing = await db.users.find_one({"email": "admin@ecommerce.com"})
    if existing:
        return

    admin_user = {
        "first_name": "Admin",
        "last_name": "User",
        "email": "admin@ecommerce.com",
        "hashed_password": hash_password("AdminPass123!"),
        "is_admin": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    await db.users.insert_one(admin_user)


if __name__ == "__main__":
    import asyncio

    asyncio.run(seed_admin_user())

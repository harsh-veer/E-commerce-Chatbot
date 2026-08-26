from datetime import datetime

import bcrypt

from app.database.client import db


def hash_password(password: str) -> str:
    pwd_bytes = password[:72].encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


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

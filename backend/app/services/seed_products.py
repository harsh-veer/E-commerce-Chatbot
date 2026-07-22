import asyncio
import json
from pathlib import Path

from app.database.client import db


async def seed_products() -> None:
    data_path = Path(__file__).parent.parent / "data" / "products.json"
    with open(data_path, "r", encoding="utf-8") as file:
        products = json.load(file)

    await db.products.delete_many({})
    if products:
        await db.products.insert_many(products)


async def main() -> None:
    await seed_products()
    print("Seeded product catalog successfully.")


if __name__ == "__main__":
    asyncio.run(main())

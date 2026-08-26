import asyncio
import json
import logging
from pathlib import Path

from app.database.client import db

logger = logging.getLogger(__name__)


async def seed_products_if_empty() -> None:
    try:
        count = await db.products.count_documents({})
        if count == 0:
            logger.info("Products collection is empty. Seeding products catalog...")
            data_path = Path(__file__).parent.parent / "data" / "products.json"
            if data_path.exists():
                with open(data_path, "r", encoding="utf-8") as file:
                    products = json.load(file)
                if products:
                    await db.products.insert_many(products)
                    logger.info(f"Seeded {len(products)} products into MongoDB.")
    except Exception as e:
        logger.warning(f"Failed to auto-seed products: {e}")


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

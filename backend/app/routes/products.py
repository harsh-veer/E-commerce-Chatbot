from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from app.database.client import db
from app.middleware.auth import require_admin
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(tags=["Products"])


def validate_object_id(id: str) -> ObjectId:
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid product id")
    return ObjectId(id)


@router.get("/", response_model=list[ProductResponse])
async def list_products():
    products = await db.products.find().to_list(100)
    return [ProductResponse.model_validate(product) for product in products]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    product = await db.products.find_one({"_id": validate_object_id(product_id)})
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return ProductResponse.model_validate(product)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_create: ProductCreate, user: dict = Depends(require_admin)):
    product = product_create.model_dump()
    product["created_at"] = product["updated_at"] = datetime.utcnow()
    result = await db.products.insert_one(product)
    created = await db.products.find_one({"_id": result.inserted_id})
    return ProductResponse.model_validate(created)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, product_update: ProductUpdate, user: dict = Depends(require_admin)):
    update_data = {k: v for k, v in product_update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No update fields provided")

    update_data["updated_at"] = __import__("datetime").datetime.utcnow()
    result = await db.products.update_one({"_id": validate_object_id(product_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    product = await db.products.find_one({"_id": validate_object_id(product_id)})
    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str, user: dict = Depends(require_admin)):
    result = await db.products.delete_one({"_id": validate_object_id(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return {"detail": "Product deleted"}

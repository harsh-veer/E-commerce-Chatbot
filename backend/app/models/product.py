from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Product(BaseModel):
    id: str | None = Field(alias="_id")
    name: str
    brand: str
    category: str
    price: float
    discount: float = 0.0
    description: str
    specifications: dict[str, str]
    rating: float = 0.0
    stock: int = 0
    images: list[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {"_id": str}

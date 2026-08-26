from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Product(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    name: str
    brand: str
    category: str
    price: float
    discount: float = 0.0
    description: str
    specifications: dict[str, str] = Field(default_factory=dict)
    rating: float = 0.0
    stock: int = 0
    images: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True)

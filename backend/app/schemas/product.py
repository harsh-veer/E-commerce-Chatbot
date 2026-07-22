from datetime import datetime

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str
    brand: str
    category: str
    price: float
    discount: float = 0.0
    description: str
    specifications: dict[str, str]
    rating: float = 0.0
    stock: int = 0
    images: list[str] = Field(default_factory=list)


class ProductUpdate(BaseModel):
    name: str | None = None
    brand: str | None = None
    category: str | None = None
    price: float | None = None
    discount: float | None = None
    description: str | None = None
    specifications: dict[str, str] | None = None
    rating: float | None = None
    stock: int | None = None
    images: list[str] | None = None
    name: str | None = None
    brand: str | None = None
    category: str | None = None
    price: float | None = None
    discount: float | None = None
    description: str | None = None
    specifications: dict[str, str] | None = None
    rating: float | None = None
    stock: int | None = None
    images: list[str] | None = None


class ProductResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    brand: str
    category: str
    price: float
    discount: float
    description: str
    specifications: dict[str, str]
    rating: float
    stock: int
    images: list[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        allow_population_by_field_name = True

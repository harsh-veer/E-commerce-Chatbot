from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: str | None = Field(alias="_id")
    first_name: str
    last_name: str
    email: EmailStr
    hashed_password: str
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {"_id": str}

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    first_name: str
    last_name: str
    email: EmailStr
    is_admin: bool
    created_at: datetime

    class Config:
        allow_population_by_field_name = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

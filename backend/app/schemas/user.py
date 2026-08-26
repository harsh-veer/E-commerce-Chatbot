from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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

    model_config = ConfigDict(populate_by_name=True)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

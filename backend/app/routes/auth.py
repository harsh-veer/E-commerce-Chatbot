from datetime import datetime, timedelta

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt

from app.config.settings import settings
from app.database.client import db
from app.schemas.user import LoginResponse, UserCreate, UserLogin, UserResponse

router = APIRouter(tags=["Authentication"])


def hash_password(password: str) -> str:
    pwd_bytes = password[:72].encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password[:72].encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@router.post("/signup", response_model=UserResponse)
async def signup(user_create: UserCreate):
    existing = await db.users.find_one({"email": user_create.email})
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = user_create.model_dump()
    user["hashed_password"] = hash_password(user.pop("password"))
    user["is_admin"] = False
    user["created_at"] = datetime.utcnow()
    user["updated_at"] = datetime.utcnow()

    result = await db.users.insert_one(user)
    created_user = await db.users.find_one({"_id": result.inserted_id})
    return UserResponse.model_validate(created_user)


@router.post("/login", response_model=LoginResponse)
async def login(user_login: UserLogin):
    user = await db.users.find_one({"email": user_login.email})
    if not user or not verify_password(user_login.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({"user_id": str(user["_id"]), "email": user["email"], "is_admin": user.get("is_admin", False)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }

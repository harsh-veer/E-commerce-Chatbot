from fastapi import APIRouter
from app.routes import auth, products, chat

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(products.router, prefix="/products")
api_router.include_router(chat.router, prefix="/chat")

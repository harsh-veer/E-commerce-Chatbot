import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.routes import api_router
from app.rag.pipeline import build_faiss as build_rag_index
from app.services.seed_users import seed_admin_user

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="AI-Powered E-commerce Product Q&A Bot",
    description="Backend API for e-commerce RAG chatbot with product management and authentication.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup_event() -> None:
    await seed_admin_user()
    await build_rag_index()


@app.get("/health")
def health_check():
    return {"status": "ok"}

import sys
import logging

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

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
    redirect_slashes=False,
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
    try:
        logger.info("Connecting to MongoDB and checking admin user...")
        await seed_admin_user()
    except Exception as e:
        logger.warning(f"Database connection warning during admin seeding: {e}. Please ensure MONGO_URI is set to your cloud MongoDB instance.")

    try:
        logger.info("Initializing RAG index...")
        await build_rag_index()
    except Exception as e:
        logger.warning(f"RAG index initialization warning: {e}")


@app.get("/health")
def health_check():
    return {"status": "ok"}

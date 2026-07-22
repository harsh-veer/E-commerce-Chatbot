from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from app.database.client import db
from app.schemas.chat import ChatRequest, ChatResponse
from app.rag.pipeline import retrieve_answer

router = APIRouter(tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(chat_request: ChatRequest):
    answer = await retrieve_answer(chat_request.question)
    if not answer:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Chat service unavailable")

    chat_item = {
        "user_id": "guest",
        "question": chat_request.question,
        "answer": answer,
        "created_at": datetime.utcnow(),
    }
    result = await db.chats.insert_one(chat_item)
    created = await db.chats.find_one({"_id": result.inserted_id})
    if created is not None:
        created["_id"] = str(created["_id"])
    return ChatResponse.model_validate(created)


@router.get("/history", response_model=list[ChatResponse])
async def chat_history():
    chats = await db.chats.find({"user_id": "guest"}).sort("created_at", -1).to_list(100)
    return [ChatResponse.model_validate(chat) for chat in chats]

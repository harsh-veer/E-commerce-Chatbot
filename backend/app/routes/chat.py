import asyncio
from datetime import datetime
import json
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from app.database.client import db
from app.schemas.chat import ChatRequest, ChatResponse
from app.rag.pipeline import retrieve_answer, retrieve_answer_stream

router = APIRouter(tags=["Chat"])


@router.post("", response_model=ChatResponse)
@router.post("/", response_model=ChatResponse)
async def chat(chat_request: ChatRequest):
    # Check if this question was already asked and has an answer
    existing_chat = await db.chats.find_one(
        {"question": chat_request.question},
        sort=[("created_at", -1)]
    )
    if existing_chat and existing_chat.get("answer"):
        cached_answer = existing_chat["answer"]
        chat_item = {
            "user_id": "guest",
            "question": chat_request.question,
            "answer": cached_answer,
            "created_at": datetime.utcnow(),
        }
        result = await db.chats.insert_one(chat_item)
        created = await db.chats.find_one({"_id": result.inserted_id})
        if created is not None:
            created["_id"] = str(created["_id"])
        return ChatResponse.model_validate(created)

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


@router.post("/stream")
async def chat_stream(chat_request: ChatRequest):
    async def event_generator():
        # Check if this question was already asked and has an answer
        existing_chat = await db.chats.find_one(
            {"question": chat_request.question},
            sort=[("created_at", -1)]
        )
        if existing_chat and existing_chat.get("answer"):
            cached_answer = existing_chat["answer"]
            # Stream the cached answer in chunks to simulate typing speed
            chunk_size = 40
            for i in range(0, len(cached_answer), chunk_size):
                chunk = cached_answer[i:i+chunk_size]
                data = json.dumps({"text": chunk})
                yield f"data: {data}\n\n"
                await asyncio.sleep(0.02)

            # Save a new chat item to history at the current time
            chat_item = {
                "user_id": "guest",
                "question": chat_request.question,
                "answer": cached_answer,
                "created_at": datetime.utcnow(),
            }
            await db.chats.insert_one(chat_item)
            return

        full_answer = []
        async for chunk in retrieve_answer_stream(chat_request.question):
            full_answer.append(chunk)
            # Send chunk in JSON-encoded format to safely handle linebreaks & markdown
            data = json.dumps({"text": chunk})
            yield f"data: {data}\n\n"
        
        # Save complete chat to database when streaming finishes
        combined_text = "".join(full_answer)
        if combined_text:
            chat_item = {
                "user_id": "guest",
                "question": chat_request.question,
                "answer": combined_text,
                "created_at": datetime.utcnow(),
            }
            await db.chats.insert_one(chat_item)

    return StreamingResponse(event_generator(), media_type="text/event-stream")



@router.get("/history", response_model=list[ChatResponse])
async def chat_history():
    chats = await db.chats.find({"user_id": "guest"}).sort("created_at", -1).to_list(100)
    for chat in chats:
        chat["_id"] = str(chat["_id"])
    return [ChatResponse.model_validate(chat) for chat in chats]


@router.delete("/history")
async def clear_chat_history():
    await db.chats.delete_many({"user_id": "guest"})
    return {"message": "Chat history cleared"}

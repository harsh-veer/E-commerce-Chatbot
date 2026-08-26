from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    question: str
    answer: str
    created_at: datetime

    model_config = ConfigDict(populate_by_name=True)

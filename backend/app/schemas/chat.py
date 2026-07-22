from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    question: str
    answer: str
    created_at: datetime

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

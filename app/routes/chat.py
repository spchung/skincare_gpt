from fastapi import APIRouter
from app.dependencies import ChatMessage

router = APIRouter()

@router.post("/chat")
async def chat(message: ChatMessage):
    return {"response": message.message}

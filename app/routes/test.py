from fastapi import APIRouter, HTTPException
from app.lang_graphs.chat_v1.main import process_chat_message_sync, process_chat_message_stream
from langchain_core.messages import HumanMessage
from typing import List
from app.lang_graphs.chat_v1.handlers import product_search_handler

router = APIRouter()

@router.post("/test")
async def test_endpoint(message: str):
    try:
        response = product_search_handler(message)
        
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

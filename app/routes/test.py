from fastapi import APIRouter, HTTPException
from app.lang_graphs.chat.main import process_chat_message_sync, process_chat_message_stream
from langchain_core.messages import HumanMessage
from typing import List
from app.lang_graphs.chat.handlers.intents.product_search import product_search_chain
from app.semantic_search.reviews import review_search

router = APIRouter()

@router.post("/test")
async def test_endpoint(message: str):
    response = review_search(message)
    return {"response": response}


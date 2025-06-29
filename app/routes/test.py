from fastapi import APIRouter, HTTPException
from app.lang_graphs.chat.main import process_chat_message_sync, process_chat_message_stream
from langchain_core.messages import HumanMessage
from langchain_core.messages import HumanMessage, AIMessage
from app.lang_graphs.chat.handlers.intents.product_search import product_search_chain
# from app.semantic_search.v1.reviews import review_search
from app.semantic_search.v2.reviews import review_search
from app.lang_graphs.chat.handlers.intents.review_search.review_search import review_search_chain


router = APIRouter()
@router.post("/test")
async def test_endpoint(message: str):
    res = review_search_chain.invoke({
        "thread_id": '123',
        "query": message,
        "messages": [],
        "sql_products": [],
        "sql_reviews": [],
    })

    return {
        "messages": [AIMessage(content=res["messages"][-1].content)],
        "intent": "review_search"
    }

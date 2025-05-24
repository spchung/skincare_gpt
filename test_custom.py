from app.memory.postgres_memory import EntityTrackingSession
from app.models.sephora import SephoraProductSQLModel, SephoraProductViewModel
from app.internal.postgres import get_db
from langchain.schema import HumanMessage, AIMessage
from app.lang_graphs.chat_v1.handlers.intents.review_search.review_search import review_search_chain
from pprint import pprint
if __name__ == '__main__':
    not_specific_query = "What are the best moisturizers for dry skin?"
    specific_query = "What do you think about the Tatcha Dewy Skin Cream? Does it work well for dry skin?"
    specific_not_found_query = "What do you think about the SkoobyDoo Cream? Is this a real product?"
    query = specific_not_found_query  # Change to not_specific_query to test the other case
    
    res = review_search_chain.invoke({
        "thread_id": '123',
        "query": query,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ],
        "sql_products": [],
        "sql_reviews": [],
    })

    pprint(res["messages"][-1].content)
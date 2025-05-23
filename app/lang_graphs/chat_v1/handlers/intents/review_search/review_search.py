from typing import List
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from typing_extensions import TypedDict
from app.semantic_search import review_search
from app.models.sephora import SephoraProductSQLModel, SephoraProductViewModel, SephoraReviewSQLModel, SephoraReviewViewModel
from app.internal.postgres import get_db
from app.lang_graphs.chat_v1.models.state import State
from app.models import QReview
from app.memory.postgres_memory import EntityTrackingSession
from app.lang_graphs.chat_v1.handlers.intents.review_search.workers.rag_worker import ReviewSearchRAGInputSchema, review_search_rag_worker
from app.lang_graphs.chat_v1.handlers.intents.review_search.workers.product_extraction_worker import product_extraction_worker, InputExtractionInputSchema, InputExtractionOutputSchema

class ReviewSearchState(TypedDict):
    messages: Annotated[Sequence[HumanMessage | AIMessage], "The messages in the conversation"]
    query: Annotated[str, "The user's query"]
    thread_id: Annotated[str, "The thread ID of the current conversation"]
    q_reviews: Annotated[List[QReview], "The reviews found in the semantic search"] | None
    sql_products: Annotated[List[SephoraProductViewModel], "The products found in the SQL search"] | None
    sql_reviews: Annotated[List[SephoraReviewViewModel], "The reviews found in the SQL search"] | None
    is_product_specific: Annotated[bool, "Whether the query is product specific"] = False
    extraction: Annotated[InputExtractionOutputSchema, "The product extraction result"] | None

def route_is_product_specific(state: ReviewSearchState):
    ''' 
    check if the query is talking about a specific product
    if so, check the EnityTrackingSession to see if the product is in the session
    if not, use normal semantic search
    '''
    query = state["query"]
    res = product_extraction_worker.run(InputExtractionInputSchema(query=query))
    state["is_product_specific"] = res.is_product_specific
    state["extraction"] = res
    return state

def handle_product_specific_search(state: ReviewSearchState):
    extraction = state["extraction"]
    if extraction is None:
        # no extraction result
        print("NO EXTRACTION RESULT")
        return state

    product_name = extraction.product_name
    brand_name = extraction.brand_name
    product_id = extraction.product_id

    print(f"product_name: {product_name}, brand_name: {brand_name}, product_id: {product_id}")

    # find product 
    db = EntityTrackingSession(next(get_db()), state["thread_id"])
    pg_product = None
    if product_id is not None:
        pg_product = db.query(SephoraProductSQLModel) \
            .filter(SephoraProductSQLModel.product_id == product_id).first()
    elif product_name is not None or brand_name is not None:
        q = db.query(SephoraProductSQLModel)
        if product_name is not None:
            q = q.filter(SephoraProductSQLModel.product_name.like(f"%{product_name}%"))
        if brand_name is not None:
            q = q.filter(SephoraProductSQLModel.brand_name.like(f"%{brand_name}%"))
        
    pg_product = q.first()
    
    if not pg_product:
        # no product found
        print("NO PRODUCT FOUND AFTER SQL SEARCH")
        return state

    # get reviews
    pg_reviews = db.query(SephoraReviewSQLModel) \
        .filter(SephoraReviewSQLModel.product_id == pg_product.product_id).all()
    
    if len(pg_reviews) == 0:
        # no reviews found
        return {
            "sql_products": [pg_product.to_pydantic()],    
        }
    
    # answer question with reviews and product
    return {
        "sql_products": [pg_product.to_pydantic()],
        "sql_reviews": [review.to_pydantic() for review in pg_reviews],
    }

def search_reviews(state: ReviewSearchState):
    # Get the query from the state
    query = state["query"]
    
    # Search for products using the semantic search
    q_reviews = review_search(query, limit=3)
    
    return {"q_reviews": q_reviews}

def get_sql_reviews(state: ReviewSearchState):
    q_reviews = state["q_reviews"]
    thread_id = state["thread_id"]
    if q_reviews is None:
        return state
    
    # db = next(get_db())
    db = EntityTrackingSession(next(get_db()), thread_id)
    # sql_products = db.query(SephoraProductSQLModel).filter(SephoraProductSQLModel.product_id.in_(product_ids)).all()
    
    # products
    product_ids = [review.product_id for review in q_reviews]
    sql_products = db.query(SephoraProductSQLModel).filter(SephoraProductSQLModel.product_id.in_(product_ids)).all()

    # reviews
    review_ids = [review.review_id for review in q_reviews]
    sql_reviews = db.query(SephoraReviewSQLModel).filter(SephoraReviewSQLModel.review_id.in_(review_ids)).all()
    
    return {
        "sql_products": [product.to_pydantic() for product in sql_products], 
        "sql_reviews": [review.to_pydantic() for review in sql_reviews]
    }

def format_response(state: ReviewSearchState):
    sql_reviews = state["sql_reviews"]
    sql_products = state["sql_products"]

    if sql_reviews is None or sql_products is None:
        return {"messages": [AIMessage(content=f"No reviews found for your query.")]}
    
    rag_response = review_search_rag_worker.run(
        ReviewSearchRAGInputSchema(query=state["query"], reviews=sql_reviews, products=sql_products))
    
    return {"messages": [AIMessage(content=rag_response.response)]}

def create_review_search_graph():
    # Create the graph
    workflow = StateGraph(ReviewSearchState)
    # Add the nodes
    workflow.add_node("route_is_product_specific", route_is_product_specific)
    workflow.add_node("handle_product_specific_search", handle_product_specific_search)
    ## TODO: add the product specific reveiw search steps
    workflow.add_node("search_reviews", search_reviews)
    workflow.add_node("get_sql_reviews", get_sql_reviews)
    workflow.add_node("format_response", format_response)
    # Set the entry point
    workflow.set_entry_point("route_is_product_specific")
    # Add edges
    workflow.add_conditional_edges(
        "route_is_product_specific",
        lambda state: "specific" if state['is_product_specific'] == True else "not_specific",
        {
            "not_specific": "search_reviews",
            "specific": "handle_product_specific_search"
        }
    )
    workflow.add_edge("search_reviews", "get_sql_reviews")
    workflow.add_edge("get_sql_reviews", "format_response")
    workflow.add_edge("handle_product_specific_search", "format_response")
    workflow.add_edge("format_response", END)
    
    # Compile the graph
    return workflow.compile()

# Create the review search chain
review_search_chain = create_review_search_graph()

def review_search_handler(state: State):
    query = state["messages"][-1].content
    res = review_search_chain.invoke({
        "thread_id": state["thread_id"],
        "query": query,
        "messages": state["messages"],
        "sql_products": [],
        "sql_reviews": [],

    })
    return {
        "messages": [AIMessage(content=res["messages"][-1].content)],
        "intent": "review_search"
    }
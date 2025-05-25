from typing_extensions import TypedDict
from typing import List, TypedDict, Annotated, Sequence
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from app.models import QReview
from app.semantic_search import review_search
from app.models.sephora import SephoraProductSQLModel, SephoraProductViewModel, SephoraReviewSQLModel, SephoraReviewViewModel
from app.internal.postgres import get_db
from app.lang_graphs.chat_v1.graph_state import MainGraphState
from app.memory.postgres_memory import EntityTrackingSession
from app.lang_graphs.chat_v1.handlers.intents.review_search. \
    workers.semantic_review_rag_worker import ReviewSearchRAGInputSchema, review_search_rag_worker
from app.lang_graphs.chat_v1.handlers.intents.review_search. \
    workers.product_extraction_worker import product_extraction_worker, InputExtractionInputSchema, InputExtractionOutputSchema
from app.lang_graphs.chat_v1.handlers.intents.review_search. \
    workers.specific_product_rag_worker import SpecificProductRecuewRAGInputSchema, specific_product_rag_worker
from app.lang_graphs.chat_v1.handlers.intents.review_search. \
    workers.specific_product_not_found_rag_worker import SpecificProdNotFoundInputSchema, specific_prod_not_found_rag_worker
from app.lang_graphs.chat_v1.handlers.vector_search_rewrite_worker import QueryRewriteInputSchema, vector_search_rewrite_agent

class ReviewSearchState(TypedDict):
    messages: Annotated[Sequence[HumanMessage | AIMessage], "The messages in the conversation"]
    query: Annotated[str, "The user's query"]
    thread_id: Annotated[str, "The thread ID of the current conversation"]
    q_reviews: Annotated[List[QReview], "The reviews found in the semantic search"] | None
    sql_products: Annotated[List[SephoraProductViewModel], "The products found in the SQL search"] | None
    sql_reviews: Annotated[List[SephoraReviewViewModel], "The reviews found in the SQL search"] | None
    is_product_specific: Annotated[bool, "Whether the query is product specific"] = False
    sprcific_product_found: Annotated[bool, "Whether the specific product was found"] = False
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
        return { "specific_product_found": False }

    product_name = extraction.product_name
    brand_name = extraction.brand_name
    product_id = extraction.product_id

    # find product 
    with EntityTrackingSession(next(get_db()), state["thread_id"]) as db:
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
            return { "specific_product_found": False }

        # get reviews
        pg_reviews = db.query(SephoraReviewSQLModel) \
            .filter(SephoraReviewSQLModel.product_id == pg_product.product_id).all()
        
        # answer question with reviews and product
        return {
            "specific_product_found": True,
            "sql_products": [pg_product.to_pydantic()],
            "sql_reviews": [review.to_pydantic() for review in pg_reviews],
        }

def semantic_search_reviews(state: ReviewSearchState):
    query = state["query"]
    rewrite_res = vector_search_rewrite_agent.run(QueryRewriteInputSchema(query=query))
    rewritten_query = rewrite_res.rewritten_query
    q_reviews = review_search(rewritten_query, limit=3)
    return {"q_reviews": q_reviews}

def get_sql_reviews(state: ReviewSearchState):
    q_reviews = state["q_reviews"]
    thread_id = state["thread_id"]

    if q_reviews is None:
        return state
    
    with EntityTrackingSession(next(get_db()), thread_id) as db:
    
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

def semantic_review_rag_response(state: ReviewSearchState):
    sql_reviews = state["sql_reviews"]
    sql_products = state["sql_products"]

    if sql_reviews is None or sql_products is None:
        return {"messages": [AIMessage(content=f"No reviews found for your query.")]}
    
    rag_response = review_search_rag_worker.run(
        ReviewSearchRAGInputSchema(query=state["query"], reviews=sql_reviews, products=sql_products))
    
    return {"messages": [AIMessage(content=rag_response.response)]}

def specific_product_rag_response(state: ReviewSearchState):
    
    sql_reviews = state["sql_reviews"]
    sql_product = state["sql_products"][0]

    res = specific_product_rag_worker.run(
        SpecificProductRecuewRAGInputSchema(
            query=state["query"],
            reviews=sql_reviews,
            product=sql_product
        )
    )
    return {"messages": [AIMessage(content=res.response)]}

def specific_product_not_found_recommendation(state: ReviewSearchState):
    query = state["query"]
    rewrite_res = vector_search_rewrite_agent.run(QueryRewriteInputSchema(query=query))
    rewritten_query = rewrite_res.rewritten_query
    q_reviews = review_search(rewritten_query, limit=3)

    # get the top 3 products and their reviews
    if not q_reviews:
        return {"messages": [AIMessage(content="No reviews found for your query.")]}
    
    product_ids = [review.product_id for review in q_reviews]
    
    products = []
    reviews = []
    
    with EntityTrackingSession(next(get_db()), state["thread_id"]) as db:
        sql_products: List[SephoraProductSQLModel] = db.query(SephoraProductSQLModel) \
            .filter(SephoraProductSQLModel.product_id.in_(product_ids)).all()
        
        # if not sql_products:
        products: List[SephoraProductViewModel] = [product.to_pydantic() for product in sql_products]
        
        # get reviews for the products
        for product in products:
            sql_reviews: List[SephoraReviewSQLModel] = db.query(SephoraReviewSQLModel) \
                .filter(SephoraReviewSQLModel.product_id == product.product_id).limit(3).all()
            
            reviews += [review.to_pydantic() for review in sql_reviews]
        
    if not products and not reviews:
        return {"messages": [AIMessage(content="No products or reviews found for your query.")]}

    return {
        "q_reviews": q_reviews,
        "sql_products": products,
        "sql_reviews": reviews,
    }

def specific_product_not_found_rag_response(state: ReviewSearchState):

    sql_reviews = state["sql_reviews"]
    sql_products = state["sql_products"]
    query = state["query"]

    res = specific_prod_not_found_rag_worker.run(
        SpecificProdNotFoundInputSchema(
            query=query,
            product=sql_products if sql_products else [],
            reviews=sql_reviews if sql_reviews else []
        )
    )
    return {"messages": [AIMessage(content=res.response)]}

def create_review_search_graph():
    # Create the graph
    workflow = StateGraph(ReviewSearchState)
    # Add the nodes
    workflow.add_node("route_is_product_specific", route_is_product_specific)
    workflow.add_node("handle_product_specific_search", handle_product_specific_search)
    
    workflow.add_node("specific_product_rag_response", specific_product_rag_response)
    workflow.add_node("specific_product_not_found_recommendation", specific_product_not_found_recommendation)
    workflow.add_node("specific_product_not_found_rag_response", specific_product_not_found_rag_response)
    
    workflow.add_node("semantic_search_reviews", semantic_search_reviews)
    workflow.add_node("get_sql_reviews", get_sql_reviews)
    workflow.add_node("semantic_review_rag_response", semantic_review_rag_response)
    # Set the entry point
    workflow.set_entry_point("route_is_product_specific")
    # Add edges
    workflow.add_conditional_edges(
        "route_is_product_specific",
        lambda state: "specific" if state['is_product_specific'] == True else "not_specific",
        {
            "not_specific": "semantic_search_reviews",
            "specific": "handle_product_specific_search"
        }
    )

    workflow.add_conditional_edges(
        "handle_product_specific_search",
        lambda state: "found" if state['specific_product_found'] == True else "not_found",
        {
            "found": "specific_product_rag_response",
            "not_found": "specific_product_not_found_recommendation"
        }
    )

    # workflow.add_edge("handle_product_specific_search", "semantic_review_rag_response")
    workflow.add_edge("semantic_search_reviews", "get_sql_reviews")
    workflow.add_edge("get_sql_reviews", "semantic_review_rag_response")
    workflow.add_edge("specific_product_not_found_recommendation", "specific_product_not_found_rag_response")
    
    workflow.add_edge("specific_product_not_found_rag_response", END)
    workflow.add_edge("semantic_review_rag_response", END)
    workflow.add_edge("specific_product_rag_response", END)
    
    # Compile the graph
    graph = workflow.compile()
    # print(graph.get_graph().draw_ascii())
    return graph

# Create the review search chain
review_search_chain = create_review_search_graph()

def review_search_handler(state: MainGraphState):
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
import instructor
from typing import List
from pydantic import Field
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from typing_extensions import TypedDict
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from app.semantic_search import review_search
from app.models.sephora import SephoraProductSQLModel, SephoraProductViewModel, SephoraReviewSQLModel, SephoraReviewViewModel
from app.internal.postgres import get_db
from app.internal.client import llm
from app.lang_graphs.chat_v1.models.state import State
from app.models import QReview

class ReviewSearchInputSchema(BaseIOSchema):
    """ ReviewSearchInputSchema """
    query: str = Field(None, description="The user's query.")
    reviews: List[SephoraReviewViewModel] = Field(None, description="The reviews found in the semantic search.")
    products: List[SephoraProductViewModel] = Field(None, description="The products found in the SQL search.")

class ReviewSearchOutputSchema(BaseIOSchema):
    """ ReviewSearchOutputSchema """
    response: str = Field(None, description="The response to the user's query.")

prompt = SystemPromptGenerator(
    background=[
        "You are an expert skincare assistant designed to help users understand how others feel about beauty products.",
        "You are provided with a list of relevant reviews and product details based on the user's query.",
        "Your goal is to summarize or extract opinions from the reviews to help the user make an informed decision.",
    ],
    steps=[
        "Carefully read the user's query to determine what information they are seeking (e.g., effectiveness, side effects, suitability for certain skin types).",
        "Review the list of matching reviews for sentiment, experiences, and recurring themes related to the query.",
        "If product information is available, consider it as helpful context for understanding the reviews (e.g., ingredients, claims, pricing).",
        "Prioritize reviews that mention the user's likely concerns (e.g., skin tone, skin type, or the problem they are targeting).",
        "Summarize key insights from the reviews clearly and concisely. Highlight any common pros or cons users mention.",
    ],
    output_instructions=[
        "Provide a helpful and specific answer to the user's query, backed by the content of the reviews.",
        "Avoid speculation—only reference information contained in the reviews or product details.",
        "If reviews are insufficient or conflicting, state that clearly and advise accordingly.",
    ]
)

worker = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(llm),
        model='gpt-4o-mini',
        temperature=0,
        input_schema=ReviewSearchInputSchema,
        output_schema=ReviewSearchOutputSchema,
        system_prompt_generator=prompt,
    ),
)

class ReviewSearchState(TypedDict):
    messages: Annotated[Sequence[HumanMessage | AIMessage], "The messages in the conversation"]
    query: Annotated[str, "The user's query"]
    q_reviews: Annotated[List[QReview], "The reviews found in the semantic search"] | None
    sql_products: Annotated[List[SephoraProductViewModel], "The products found in the SQL search"] | None
    sql_reviews: Annotated[List[SephoraReviewViewModel], "The reviews found in the SQL search"] | None

def search_reviews(state: ReviewSearchState):
    # Get the query from the state
    query = state["query"]
    
    # Search for products using the semantic search
    q_reviews = review_search(query, limit=3)
    
    return {"q_reviews": q_reviews}


def get_sql_reviews(state: ReviewSearchState):
    q_reviews = state["q_reviews"]
    if q_reviews is None:
        return state
    
    db = next(get_db())
    
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
    
    rag_response = worker.run(ReviewSearchInputSchema(query=state["query"], reviews=sql_reviews, products=sql_products))
    
    return {"messages": [AIMessage(content=rag_response.response)]}

def create_review_search_graph():
    # Create the graph
    workflow = StateGraph(ReviewSearchState)
    
    # Add the nodes
    workflow.add_node("search_reviews", search_reviews)
    workflow.add_node("get_sql_reviews", get_sql_reviews)
    workflow.add_node("format_response", format_response)
    
    # Set the entry point
    workflow.set_entry_point("search_reviews")

    # Add edges
    workflow.add_edge("search_reviews", "get_sql_reviews")
    workflow.add_edge("get_sql_reviews", "format_response")
    workflow.add_edge("format_response", END)
    
    # Compile the graph
    return workflow.compile()

# Create the review search chain
review_search_chain = create_review_search_graph()

def review_search_handler(state: State):
    query = state["messages"][-1].content
    res = review_search_chain.invoke({
        "query": query,
        "messages": state["messages"]
    })
    return {
        "messages": [AIMessage(content=res["messages"][-1].content)],
        "intent": "review_search"
    }
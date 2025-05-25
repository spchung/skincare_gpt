import instructor
from pydantic import Field
from typing import List, TypedDict, Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from app.internal.client import llm
from app.internal.postgres import get_db
from app.lang_graphs.chat_v1.graph_state import MainGraphState
from app.models.sephora import SephoraProductSQLModel, SephoraProductViewModel
from app.semantic_search.products import product_search
from app.memory.postgres_memory import EntityTrackingSession
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator

class ProductSearchRAGInputSchema(BaseIOSchema):
    """ ProductSearchRAGInputSchema """
    query: str = Field(None, description="The user's query.")
    products: List[SephoraProductViewModel] = Field(None, description="The products found in the semantic search.")

class ProductSearchRAGOutputSchema(BaseIOSchema):
    """ ProductSearchRAGOutputSchema """
    response: str = Field(None, description="The RAG response to the user's query.")

prompt = SystemPromptGenerator(
    background=[
        "You are an expert skincare shopping assistant powered by a retrieval-augmented generation (RAG) system.",
        "You receive the user's query along with a list of semantically matched skincare products.",
        "Each product includes attributes such as name, brand, price, size, rating, number of reviews, and category hierarchy.",
        "Your goal is to help users make informed purchasing decisions by clearly summarizing and comparing the relevant products returned by the system."
    ],
    steps=[
        "Read and understand the user's query to determine the kind of product information they are looking for (e.g., budget options, best-rated, by category, etc.).",
        "Review the list of products retrieved from the vector search. Extract useful information such as product name, brand, price, size, and rating.",
        "Summarize the most relevant products in a helpful and concise way. Highlight the strengths or standout features of each item when appropriate.",
        "If possible, recommend a top product or a few options tailored to the user's intent (e.g., best value, best-reviewed, most popular).",
    ],
    output_instructions=[
        "Write a conversational response that directly answers the user's query based on the retrieved products.",
        "Avoid repeating product IDs or internal field names unless helpful to the user.",
        "Maintain a friendly, knowledgeable tone and avoid making up any product details.",
        "If no relevant products are found, politely explain that and offer to refine the search."
    ]
)

worker = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(llm),
        model='gpt-4o-mini',
        temperature=0,
        input_schema=ProductSearchRAGInputSchema,
        output_schema=ProductSearchRAGOutputSchema,
        system_prompt_generator=prompt,
    ),
)

# Graph
class ProductSearchState(TypedDict):
    messages: Annotated[Sequence[HumanMessage | AIMessage], "The messages in the conversation"]
    query: Annotated[str, "The user's query"]
    product_ids: Annotated[List[str], "The products found in the semantic search"] | None
    sql_products: Annotated[List[SephoraProductViewModel], "The products found in the SQL search"] | None
    thread_id: Annotated[str, "The thread ID of the current conversation"]

def search_products(state: ProductSearchState):
    # Get the query from the state
    query = state["query"]
    
    # Search for products using the semantic search
    products = product_search(query, limit=3)
    
    # Format the results
    if not products:
        return state
    
    product_ids = [product.product_id for product in products]
    return {"product_ids": product_ids}

def get_sql_product(state: ProductSearchState):
    product_ids = state["product_ids"]
    thread_id = state["thread_id"]
    
    if product_ids is None:
        return state
    
    with EntityTrackingSession(next(get_db()), thread_id) as db:
        sql_products = db.query(SephoraProductSQLModel).filter(SephoraProductSQLModel.product_id.in_(product_ids)).all()
        return {"sql_products": [product.to_pydantic() for product in sql_products]}

def format_response(state: ProductSearchState):
    sql_products = state["sql_products"]
    if sql_products is None:
        return {"messages": [AIMessage(content=f"No products found for your query.")]}
    
    rag_response = worker.run(ProductSearchRAGInputSchema(query=state["query"], products=sql_products))
    return {"messages": [AIMessage(content=rag_response.response)]}

def create_product_search_graph():
    # Create the graph
    workflow = StateGraph(ProductSearchState)
    
    # Add the nodes
    workflow.add_node("search_products", search_products)
    workflow.add_node("get_sql_product", get_sql_product)
    workflow.add_node("format_response", format_response)
    
    # Set the entry point
    workflow.set_entry_point("search_products") 
    
    # Add edges
    workflow.add_edge("search_products", "get_sql_product")
    workflow.add_edge("get_sql_product", "format_response")
    workflow.add_edge("format_response", END)
    
    # Compile the graph
    return workflow.compile()

# Create the product search chain
product_search_chain = create_product_search_graph()

def product_search_handler(state: MainGraphState):
    query = state["messages"][-1].content
    thread_id = state["thread_id"]
    
    res = product_search_chain.invoke({
        "query": query,
        "messages": state["messages"],
        "thread_id": thread_id
    })
    return {
        "messages": [AIMessage(content=res["messages"][-1].content)],
        "intent": "product_search"
    }
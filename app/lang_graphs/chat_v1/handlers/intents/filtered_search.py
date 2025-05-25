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
from app.semantic_search.products import product_filtered_search
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from app.lang_graphs.chat_v1.models.filtered_search import ProductSearchFilter
from app.lang_graphs.chat_v1.handlers.intents.product_search import ProductSearchRAGInputSchema, worker as product_rag_output_worker

class FilterExtractInputSchema(BaseIOSchema):
    """ FilterExtractInputSchema """
    query: str = Field(None, description="The user's query.")

class FilterExtractOutputSchema(BaseIOSchema):
    """ FilterExtractOutputSchema """
    extracted_filters: List[ProductSearchFilter] = Field(None, description="The extracted filters from the user's query.")

prompt = SystemPromptGenerator(
    background=[
        "You are a filter extraction agent that identifies structured filter criteria from user queries in a shopping assistant.",
        "You only support two types of filters: 'price' and 'rating'.",
        "Each filter must include three parts: the filter type, the directional condition ('above' or 'below'), and the numeric value associated with the condition.",
        "This information is used to constrain product search results based on user preferences."
    ],
    steps=[
        "Read the user's query carefully.",
        "Determine if the user is referring to a price constraint (e.g., 'under $50', 'more than 30 dollars') or a rating constraint (e.g., 'at least 4 stars', 'less than 3').",
        "For each constraint identified, extract:",
        "  - The filter type ('price' or 'rating'),",
        "  - The filter condition: 'above' for expressions like 'at least', 'more than', or 'higher than'; 'below' for expressions like 'under', 'less than', or 'no more than',",
        "  - The numeric value mentioned in the query (e.g., 50, 4).",
        "Ignore any constraints that are not related to 'price' or 'rating' or do not clearly specify a numeric value and condition.",
        "Example: For query 'Show me products under $50 with at least 4 stars', return:",
        "  [{'filter_type': 'price', 'filter_condition': 'below', 'filter_value': 50},",
        "    {'filter_type': 'rating', 'filter_condition': 'above', 'filter_value': 4}]"
    ],
    output_instructions=[
        "Return a list of extracted filters, each containing:",
        "  - 'filter_type': either 'price' or 'rating',",
        "  - 'filter_condition': either 'above' or 'below',",
        "  - 'filter_value': the numeric threshold mentioned in the query.",
        "Only include a filter if all three components are clearly present in the query.",
        "Do not guess or infer missing values. If the query is ambiguous or incomplete, omit the filter.",
        "Do not extract or include any filters other than 'price' or 'rating'."
    ]
)

extract_filters_worker = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(llm),
        model='gpt-4o-mini',
        temperature=0,
        input_schema=FilterExtractInputSchema,
        output_schema=FilterExtractOutputSchema,
        system_prompt_generator=prompt,
    ),
)

# Graph
class FilteredSearchState(TypedDict):
    messages: Annotated[Sequence[HumanMessage | AIMessage], "The messages in the conversation"]
    query: Annotated[str, "The user's query"]
    filters: Annotated[List[ProductSearchFilter], "The extracted filters from the query"] | None
    product_ids: Annotated[List[str], "The products found in the semantic search"] | None
    sql_products: Annotated[List[SephoraProductViewModel], "The products found in the SQL search"] | None

def extract_filters(state: FilteredSearchState):
    # Get the query from the state
    query = state["query"]
    
    # Extract filters using the worker
    filter_response = extract_filters_worker.run(FilterExtractInputSchema(query=query))
    
    print(filter_response.extracted_filters)
    return {"filters": filter_response.extracted_filters}

def search_products(state: FilteredSearchState):
    # Get the query and filters from the state
    query = state["query"]
    filters = state["filters"]
    
    products = product_filtered_search(query, limit=3, product_search_filters=filters)
    return {"product_ids": [product.product_id for product in products]}

def get_sql_product(state: FilteredSearchState):
    product_ids = state["product_ids"]
    if product_ids is None:
        return state
    
    db = next(get_db())
    sql_products = db.query(SephoraProductSQLModel).filter(SephoraProductSQLModel.product_id.in_(product_ids)).all()
    return {"sql_products": [product.to_pydantic() for product in sql_products]}

def format_response(state: FilteredSearchState):
    sql_products = state["sql_products"]
    if sql_products is None:
        return {"messages": [AIMessage(content=f"No products found matching your filters.")]}
    
    rag_response = product_rag_output_worker.run(ProductSearchRAGInputSchema(query=state["query"], products=sql_products))
    
    return {"messages": [AIMessage(content=rag_response.response)]}

def create_filtered_search_graph():
    # Create the graph
    workflow = StateGraph(FilteredSearchState)
    
    # Add the nodes
    workflow.add_node("extract_filters", extract_filters)
    workflow.add_node("search_products", search_products)
    workflow.add_node("get_sql_product", get_sql_product)
    workflow.add_node("format_response", format_response)
    
    # Set the entry point
    workflow.set_entry_point("extract_filters")
    
    # Add edges
    workflow.add_edge("extract_filters", "search_products")
    workflow.add_edge("search_products", "get_sql_product")
    workflow.add_edge("get_sql_product", "format_response")
    workflow.add_edge("format_response", END)
    
    # Compile the graph
    return workflow.compile()

# Create the filtered search chain
filtered_search_chain = create_filtered_search_graph()

def filtered_search_handler(state: MainGraphState):
    query = state["messages"][-1].content
    res = filtered_search_chain.invoke({
        "query": query,
        "messages": state["messages"]
    })
    return {
        "messages": [AIMessage(content=res["messages"][-1].content)],
        "intent": "filter_search"
    }


from typing import List
from langgraph.graph import StateGraph, START, END
from .memory.thread_context import ThreadContextStore
from langchain_core.messages import HumanMessage, AIMessage
from .handlers.basic_questioinaire import questionnaire_handler, is_questionnaire_complete
from app.lang_graphs.chat.graph_state import MainGraphState
from .handlers.chat_loop import chat_handler
from langchain.chat_models import init_chat_model
from app.lang_graphs.chat.handlers import (
    intent_classification_router, 
    other_handler,
    product_search_handler,
    review_search_handler,
    filtered_search_handler,
    follow_up_question_handler
)  

llm = init_chat_model("openai:gpt-4o-mini")
## temp - be replaced with redis
thread_context_store = ThreadContextStore()

# Initialize graph
graph_builder = StateGraph(MainGraphState)

## utility nodes
def questionnaire_router(state: MainGraphState):
    if state['questionnaire_complete']:
        return { "questionnaire_complete": True}
    return { "questionnaire_complete": is_questionnaire_complete(state['questionnaire']) }

# build graph
graph_builder.add_node("questionnaire_router", questionnaire_router)
graph_builder.add_node("questionnaire_handler", questionnaire_handler)
graph_builder.add_node("intent_classification_router", intent_classification_router)
graph_builder.add_node("chat_handler", chat_handler)
graph_builder.add_node("other_handler", other_handler)
graph_builder.add_node("product_search_handler", product_search_handler)
graph_builder.add_node("review_search_handler", review_search_handler)
graph_builder.add_node("filtered_search_handler", filtered_search_handler)
graph_builder.add_node("follow_up_handler", follow_up_question_handler)

graph_builder.add_edge(START, "questionnaire_router")
graph_builder.add_conditional_edges(
    "questionnaire_router", 
    lambda state: "intent_classification_router" if state['questionnaire_complete'] else "questionnaire_handler",
    {
        "intent_classification_router": "intent_classification_router",
        "questionnaire_handler": "questionnaire_handler",
    }
)

# graph_builder.add_edge("questionnaire_handler", "intent_classification_router")
graph_builder.add_conditional_edges(
    "intent_classification_router",
    lambda state: state['intent'],
    {
        "product_search": "product_search_handler",
        "review_search": "review_search_handler",
        "filter_search": "filtered_search_handler",
        "other": "other_handler",
        'follow_up': "follow_up_handler",  # Assuming follow-up_handler is defined elsewhere
    }
)
graph_builder.add_edge("questionnaire_handler", END)
graph_builder.add_edge("chat_handler", END)
graph_builder.add_edge("other_handler", END)
graph_builder.add_edge("product_search_handler", END)
graph_builder.add_edge("review_search_handler", END)
graph_builder.add_edge("filtered_search_handler", END)
graph = graph_builder.compile()

# Invocation
def process_chat_message_sync(messages: List[AIMessage|HumanMessage], session_id: str):
    questionnaire_form = thread_context_store.get_thread_context(session_id).questionnaire
    res = graph.invoke({
        "messages": messages, 
        "thread_id": session_id,
        "questionnaire": questionnaire_form,
        "questionnaire_complete": True, ## skip for testing
    })

    return res["messages"][-1]

# Streaming version
async def process_chat_message_stream(messages: List[AIMessage|HumanMessage], session_id: str):
    questionnaire_form = thread_context_store.get_thread_context(session_id).questionnaire
    for event in graph.stream({
        "messages": messages, 
        "thread_id": session_id,
        "questionnaire": questionnaire_form,
        "questionnaire_complete": True, ## skip for testing
    }):
        for value in event.values():
            if "messages" in value:
                yield value["messages"][-1].content
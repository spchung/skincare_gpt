from typing import Annotated, List
from langgraph.graph import StateGraph, START, END
from .memory.thread_context import ThreadContextStore
from langchain_core.messages import HumanMessage, AIMessage
from .handlers.basic_questioinaire import questionnaire_handler, is_questionnaire_complete
from .models.state import State
from .handlers.chat_loop import chat_handler
from langchain.chat_models import init_chat_model
from app.lang_graphs.chat_v1.handlers import (
    intent_classification_router, 
    other_handler
)  

llm = init_chat_model("openai:gpt-4o-mini")
## temp - be replaced with redis
thread_context_store = ThreadContextStore()

# Initialize graph
graph_builder = StateGraph(State)

## utility nodes
def questionnaire_router(state: State):
    if state['questionnaire_complete']:
        return { "questionnaire_complete": True}
    return { "questionnaire_complete": is_questionnaire_complete(state['questionnaire']) }

def decision_router(state: State):
    if state['questionnaire_complete']:
        return "intent_classification_router"
    return "questionnaire_handler"



# build graph
graph_builder.add_node("questionnaire_router", questionnaire_router)
graph_builder.add_node("questionnaire_handler", questionnaire_handler)
graph_builder.add_node("intent_classification_router", intent_classification_router)
graph_builder.add_node("chat_handler", chat_handler)
graph_builder.add_node("other_handler", other_handler)
## todo
# graph_builder.add_node("product_search_handler", chat_handler)
# graph_builder.add_node("review_search_handler", chat_handler)
# graph_builder.add_node("compare_handler", chat_handler)
# graph_builder.add_node("filter_search_handler", chat_handler)

graph_builder.add_edge(START, "questionnaire_router")
graph_builder.add_conditional_edges(
    "questionnaire_router", 
    decision_router,
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
        "product_search": "chat_handler",
        "review_search": "chat_handler",
        "compare": "chat_handler",
        "filter_search": "chat_handler",
        "other": "other_handler",
    }
)
graph_builder.add_edge("questionnaire_handler", END)
graph_builder.add_edge("chat_handler", END)
graph_builder.add_edge("other_handler", END)


graph = graph_builder.compile()

# Invocation
def process_chat_message_sync(messages: List[AIMessage|HumanMessage], session_id: str):
    questionnaire_form = thread_context_store.get_thread_context(session_id).questionnaire
    res = graph.invoke({
        "messages": messages, 
        "thread_id": session_id,
        "questionnaire": questionnaire_form,
        "questionnaire_complete": is_questionnaire_complete(questionnaire_form),
    })

    return res["messages"][-1]

# Streaming version
async def process_chat_message_stream(messages: List[AIMessage|HumanMessage], session_id: str):
    questionnaire_form = thread_context_store.get_thread_context(session_id).questionnaire
    for event in graph.stream({
        "messages": messages, 
        "thread_id": session_id,
        "questionnaire": questionnaire_form,
        "questionnaire_complete": is_questionnaire_complete(questionnaire_form),
    }):
        for value in event.values():
            if "messages" in value:
                yield value["messages"][-1].content
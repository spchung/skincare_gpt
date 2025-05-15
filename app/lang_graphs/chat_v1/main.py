from typing import Annotated, List
from langgraph.graph import StateGraph, START, END
from .memory.thread_context import ThreadContextStore
from langchain_core.messages import HumanMessage, AIMessage
from .handlers.basic_questioinaire import questionnaire_handler, is_questionnaire_complete
from .models.state import State
from app.context.manager import trim_messages
from .handlers.chat_loop import chat_handler
from langchain.chat_models import init_chat_model
llm = init_chat_model("openai:gpt-4o-mini")

## temp - be replaced with redis
thread_context_store = ThreadContextStore()

# Initialize graph
graph_builder = StateGraph(State)

## utility nodes
def init_node(state: State):
    '''
    This node is for anthing that needs to be done before the chat starts.
    '''
    return {
        "messages": trim_messages(state['messages']),
    }

def call_question_router(state: State):
    if state['questionnaire_complete']:
        return {
            "questionnaire_complete": True,
        }
    
    questionnaire = state['questionnaire']
    
    return {
        "questionnaire_complete": is_questionnaire_complete(questionnaire),
        "questionnaire": questionnaire,
    }

def decision_router(state: State):
    if state['questionnaire_complete']:
        return "main_handler"
    return "questionnaire_handler"

# build graph
graph_builder.add_node("call_question_router", call_question_router)
graph_builder.add_node("questionnaire_handler", questionnaire_handler)
graph_builder.add_node("chat_handler", chat_handler)

graph_builder.add_edge(START, "call_question_router")

graph_builder.add_conditional_edges(
    "call_question_router", 
    decision_router,
    {
        "chat_handler": "chat_handler",
        "questionnaire_handler": "questionnaire_handler",
    }
)

graph_builder.add_edge("questionnaire_handler", END)
graph_builder.add_edge("chat_handler", END)
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
    
    thread_context_store.info()

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
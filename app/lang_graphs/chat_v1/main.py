from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from .memory.thread_context import ThreadContextStore
from langchain_core.messages import HumanMessage, AIMessage
from .handlers.basic_questioinaire import (
    BasicQuestionaireModel, 
    get_next_question, 
    answer_field, 
    get_init_question,
    is_form_complete
)

## temp - be replaced with redis
thread_context_store = ThreadContextStore()

# State
class State(TypedDict):
    messages: Annotated[list, add_messages]
    session_id: str
    questionnaire: BasicQuestionaireModel
    questionnaire_complete: bool

# Initialize graph
graph_builder = StateGraph(State)
from langchain.chat_models import init_chat_model

llm = init_chat_model("openai:gpt-4o-mini")


# transition functions


## nodes

def questionnaire_handler(state: State):
    """Process the questionnaire state and determine next action"""
    if state['questionnaire'] is None:
        raise ValueError("Questionnaire not found in state")
    
    questionnaire = state['questionnaire']
    
    # Get the last user message
    last_message = state['messages'][-1]
    if not isinstance(last_message, HumanMessage):
        raise ValueError("Last message is not a human message")
    
    if is_form_complete(questionnaire):
        ## Tell user already completed
        pass

    # Process the answer if we have a current field
    if not questionnaire.current_field:
        ## init questionnaire
        init_question, _ = get_init_question(questionnaire)
        return {
            "messages": [AIMessage(content=init_question)],
            "questionnaire": questionnaire,
        }
        
    questionnaire = answer_field(
        questionnaire, 
        questionnaire.current_field, 
        last_message.content
    )

    question, _ = get_next_question(questionnaire)
    # save thread context
    thread_context_store.set_thread_questionnaire(state['session_id'], questionnaire)
    
    # exit 
    if is_form_complete(questionnaire):
        return {
            "messages": [AIMessage(content=" Great! Thank you for completing the questionnaire!")],
            "questionnaire": questionnaire,
        }

    return {
        "messages": [AIMessage(content=question)],
        "questionnaire": questionnaire,
    }

def main_handler(state: State):
    
    return {
        "messages": [AIMessage(content="You made it son!")],
    }

def call_question_router(state: State):
    session_id = state['session_id']
    questionnaire = thread_context_store.get_thread_context(session_id).questionnaire
    
    return {
        "questionnaire_complete": is_form_complete(questionnaire),
        "questionnaire": questionnaire,
    }

def decision_router(state: State):
    if state['questionnaire_complete']:
        return "main_handler"
    return "questionnaire_handler"

# build graph
graph_builder.add_node("questionnaire_handler", questionnaire_handler)
graph_builder.add_node("main_handler", main_handler)
graph_builder.add_node("call_question_router", call_question_router)

graph_builder.add_edge(START, "call_question_router")

graph_builder.add_conditional_edges(
    "call_question_router", 
    decision_router,
    {
        "main_handler": "main_handler",
        "questionnaire_handler": "questionnaire_handler",
    }
)

graph_builder.add_edge("questionnaire_handler", END)
graph_builder.add_edge("main_handler", END)
graph = graph_builder.compile()

# Invocation
def process_chat_message_sync(messages: List[AIMessage|HumanMessage], session_id: str):
    
    thread_context_store.info()
    questionnaire_form = thread_context_store.get_thread_context(session_id).questionnaire
    
    res = graph.invoke({
        "messages": messages, 
        "session_id": session_id,
        "questionnaire": questionnaire_form,
        "current_field": None
    })

    return res["messages"][-1]

# Streaming version
async def process_chat_message_stream(messages: List[AIMessage|HumanMessage], session_id: str):
    
    thread_context_store.info()

    questionnaire_form = thread_context_store.get_thread_context(session_id).questionnaire
    
    for event in graph.stream({
        "messages": messages, 
        "session_id": session_id,
        "questionnaire": questionnaire_form,
        "current_field": None
    }):
        for value in event.values():
            if "messages" in value:
                yield value["messages"][-1].content
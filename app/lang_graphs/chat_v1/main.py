from typing import Annotated, Dict, Any, List
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from .handlers.basic_questioinaire import (
    BasicQuestionaireModel, 
    get_next_question, 
    answer_field,
    get_init_question
)
from .memory.thread_context import ThreadContextStore

## temp - be replaced with redis
thread_context_store = ThreadContextStore()

# State
class State(TypedDict):
    messages: Annotated[list, add_messages]
    session_id: str
    questionnaire: BasicQuestionaireModel

# Initialize graph
graph_builder = StateGraph(State)
from langchain.chat_models import init_chat_model

llm = init_chat_model("openai:gpt-4o-mini")

## nodes
def process_questionnaire(state: State):
    """Process the questionnaire state and determine next action"""
    if state['questionnaire'] is None:
        raise ValueError("Questionnaire not found in state")
    
    questionnaire = state['questionnaire']
    
    # Get the last user message
    last_message = state['messages'][-1]
    if isinstance(last_message, HumanMessage):
        # Process the answer if we have a current field
        if questionnaire.current_field:
            questionnaire = answer_field(
                questionnaire, 
                questionnaire.current_field, 
                last_message.content
            )

        else:
            ## init questionnaire
            init_question, init_field = get_init_question(questionnaire)

            return {
                "messages": [AIMessage(content=init_question)],
                "questionnaire": questionnaire,
                "current_field": init_field
            }
    
    # Get next question
    question, field = get_next_question(state['questionnaire'])

    # save thread context
    thread_context_store.set_thread_questionnaire(state['session_id'], state['questionnaire'])
    
    thread_context_store.info()

    # Add response to messages
    return {
        "messages": [AIMessage(content=question)],
        "questionnaire": state['questionnaire'],
        "current_field": field
    }

# build graph
graph_builder.add_node("questionnaire_state", process_questionnaire)
graph_builder.add_edge(START, "questionnaire_state")
graph_builder.add_edge("questionnaire_state", END)

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
    print(questionnaire_form)
    
    for event in graph.stream({
        "messages": messages, 
        "session_id": session_id,
        "questionnaire": questionnaire_form,
        "current_field": None
    }):
        for value in event.values():
            if "messages" in value:
                yield value["messages"][-1].content
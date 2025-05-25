'''
Other intent shoudld be handled with suggested questions to ask the user.
'''
from pydantic import Field
from app.internal.client import llm
import instructor
from app.lang_graphs.chat_v1.graph_state import MainGraphState
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, END
from typing import Annotated, Sequence, TypedDict
from .workers import (
    unknown_intent_worker, other_intent_classifier_worker, greeting_intent_worker,
    UnknownIntentInputSchema, OtherIntentClassifierInputSchema, GreetingIntentInputSchema
)
from langgraph.graph.message import add_messages

class OtherIntentState(TypedDict):
    messages: Annotated[list, add_messages]
    query: str
    intent: str 

# Add the nodes
def other_intent_classifier_handler(state):
    res = other_intent_classifier_worker.run(OtherIntentClassifierInputSchema(query=state['query']))
    return { "intent": res.intent }
    
def unknown_intent_handler(state):
    res = unknown_intent_worker.run(UnknownIntentInputSchema(query=state['query']))
    response = res.response
    return { "messages": [AIMessage(content=response)] }
    
def greeting_intent_handler(state):
    res = greeting_intent_worker.run(GreetingIntentInputSchema(query=state['query']))
    response = res.response
    return { "messages": [AIMessage(content=response)] }

def create_other_graph():
    # Create the graph
    workflow = StateGraph(OtherIntentState)
    
    workflow.add_node("other_intent_classifier", other_intent_classifier_handler)
    workflow.add_node("unknown_intent", unknown_intent_handler) 
    workflow.add_node("greeting_intent", greeting_intent_handler)
    
    # Set the entry point
    workflow.set_entry_point("other_intent_classifier")
    
    # Add edges
    workflow.add_conditional_edges(
        "other_intent_classifier",
        lambda state: state["intent"],
        {
            "greeting": "greeting_intent",
            "unknown": "unknown_intent"
        }
    )
    workflow.add_edge("greeting_intent", END)
    workflow.add_edge("unknown_intent", END)
    return workflow.compile()

# Create the other intent chain
other_chain = create_other_graph()

def other_handler(state: MainGraphState):
    query = state["messages"][-1].content
    res = other_chain.invoke({ 
        "query": query,
        "messages": state['messages']
    })

    message = res['messages'][-1].content
    return { "messages": [AIMessage(content=message)] }

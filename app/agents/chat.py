from typing import Annotated, Dict, Any, List

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
# from app.routes.chat import MessagesPayload

## NOTE: this state does not persist across requests.
## Conversation history needs to be handled by the client.
class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)
from langchain.chat_models import init_chat_model

llm = init_chat_model("openai:gpt-4o-mini")

## nodes
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

def return_last_message(state: State):
    return {"messages": [state["messages"][-1]]}

# build graph
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("return_last_message", return_last_message)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", "return_last_message")
graph_builder.add_edge("return_last_message", END)

graph = graph_builder.compile()

# no streaming
def process_chat_message_no_stream(messages: List[AIMessage|HumanMessage], session_id: str):
    res = graph.invoke({"messages": messages})
    res = res["messages"][-1]
    return res

# streaming
async def process_chat_message_stream(messages: list, session_id: str):
    for event in graph.stream({"messages": messages}):
        for value in event.values():
            content = value["messages"][-1].content
            if isinstance(content, str):
                yield content
            else:
                yield str(content)
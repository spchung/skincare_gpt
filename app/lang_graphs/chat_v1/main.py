from typing import Annotated, Dict, Any, List
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage

from .handlers.basic_questioinaire import BasicQuestionaireModel

# State
class State(TypedDict):
    messages: Annotated[list, add_messages]
    session_id: str

# graph definition
graph_builder = StateGraph(State)
from langchain.chat_models import init_chat_model

llm = init_chat_model("openai:gpt-4o-mini")

## nodes

# 0. Basic Questionaire
def basic_questionaire(state: State):
    struct_llm = llm.with_structured_output(BasicQuestionaireModel)
    output = struct_llm.invoke(state["messages"])
    print(output)
    return {"messages": [output]}

# # 1. Reshape Question (if needed)
# def reshape_question(state: State):
#     return {"messages": [llm.invoke(state["messages"])]}

# # 2. Intnet Classification
# def classify_intent(state: State):
#     return {"messages": [llm.invoke(state["messages"])]}


# build graph
graph_builder.add_node("basic_questionaire", basic_questionaire)
# graph_builder.add_node("reshape_question", reshape_question)
# graph_builder.add_node("classify_intent", classify_intent)


graph_builder.add_edge(START, "basic_questionaire")
graph_builder.add_edge("basic_questionaire", END)

graph = graph_builder.compile()


# Invocation
def process_chat_message_no_stream(messages: List[AIMessage|HumanMessage], session_id: str):
    res = graph.invoke({"messages": messages, "session_id": session_id})
    res = res["messages"][-1]
    return res

if __name__ == "__main__":
    # user question form
    questionaire_form = BasicQuestionaireModel()
    
    # init_question = 
    messages = [HumanMessage(content="Hello, how are you?")]
    res = process_chat_message_no_stream(messages, "123")
    print(res)
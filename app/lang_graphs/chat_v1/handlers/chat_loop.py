from typing import Optional, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from app.lang_graphs.chat_v1.models.state import State
from app.lang_graphs.chat_v1.memory.thread_context import get_context_store

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def init_message_handler(state: State):
    '''
    After the questionnaire is complete, the user will be greeted with a message.
    '''
    return {
        "messages": [AIMessage(content="You made it son!")],
    }

def chat_handler(state: State):
    return {
        "messages": [AIMessage(content="You made it son!")],
    }
from openai import OpenAI
import streamlit as st
import torch
from dotenv import load_dotenv
load_dotenv()

torch.classes.__path__ = [] # to avoid streamlit error message

from app.lang_graphs.chat.main import process_chat_message_sync, process_chat_message_stream
from langchain_core.messages import HumanMessage, AIMessage

with st.sidebar:
    # openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    name = st.text_input("Name", key="chatbot_name")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 Skincare GPT")
st.caption("🚀 Your personalized skincare assistant")

if "messages" not in st.session_state:
    st.session_state["messages"] = [AIMessage(content="Hello! Welcome to Skincare GPT. I'm here to help you with your skincare questions and concerns. How can I help you today?")]

for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    else:
        st.chat_message("assistant").write(msg.content)

if prompt := st.chat_input():

    user_msg = HumanMessage(content=prompt)
    st.session_state.messages.append(user_msg)
    st.chat_message("user").write(prompt)

    msgs = st.session_state.messages
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_msg = process_chat_message_sync(msgs, '123')
            st.session_state.messages.append(response_msg)
            st.write(response_msg.content)
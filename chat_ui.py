from dotenv import load_dotenv
load_dotenv()

from app.lang_graphs.chat.main import process_chat_message_sync
from langchain_core.messages import HumanMessage, AIMessage

import streamlit as st

st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by OpenAI")

if "messages" not in st.session_state:
    st.session_state["messages"] = [AIMessage(content="Hello! Welcome to Skincare GPT. I'm here to help you with your skincare questions and concerns. How can I help you today?")]

# Display existing messages
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    else:
        st.chat_message("assistant").write(msg.content)

if prompt := st.chat_input():
    user_msg = HumanMessage(content=prompt)
    st.session_state.messages.append(user_msg)
    st.chat_message("user").write(prompt)
    
    with st.chat_message("assistant"), st.empty():
        with st.spinner("Thinking..."):
            msg = process_chat_message_sync(st.session_state.messages, '123')
        st.write(msg.content)
    
    st.session_state.messages.append(AIMessage(content=msg.content))
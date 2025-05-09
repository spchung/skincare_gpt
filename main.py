from fastapi import FastAPI
from app.routes import chat

app = FastAPI()

# Include the chat router
app.include_router(chat.router, prefix="/chat", tags=["chat"])

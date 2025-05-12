from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

router = APIRouter()

class ChatRequestBody(BaseModel):
    message: str
    session_id: str

def stream_chat_response(message: str):
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": message}],
            temperature=0.7,
            max_tokens=1000,
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        yield f"Error: {str(e)}"

@router.post("/chat")
def stream(body: ChatRequestBody):
    return StreamingResponse(
        stream_chat_response(body.message),
        media_type="text/event-stream"
    )

@router.post("/chat_no_stream")
async def chat_no_stream(body: ChatRequestBody):
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": body.message}],
            temperature=0.7,
            max_tokens=1000,
            stream=False
        )
        
        return {
            "response": response.choices[0].message.content,
            "session_id": body.session_id
        }
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
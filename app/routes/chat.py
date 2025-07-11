import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.websockets import WebSocketState
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
from app.lang_graphs.chat.main import process_chat_message_stream, process_chat_message_sync
import logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)


# Load environment variables
load_dotenv()

router = APIRouter()

class ChatRequestBody(BaseModel):
    message: str
    session_id: str

class Content(BaseModel):
    type: str
    text: str

class Status(BaseModel):
    type: str
    reason: Optional[str] = None

class Metadata(BaseModel):
    custom: Dict[str, Any]
    unstable_annotations: Optional[List[Any]] = None
    unstable_data: Optional[List[Any]] = None
    steps: Optional[List[Any]] = None

class Message(BaseModel):
    id: str
    createdAt: str
    role: str
    content: List[Content]
    attachments: Optional[List[Any]] = []
    metadata: Metadata
    status: Optional[Status] = None


class MessagesPayload(BaseModel):
    messages: List[Message]

class MessagesPayload(BaseModel):
    messages: List[Message]

## helpers
def convert_frontend_messages_to_langchain(messages: List[Message]) -> List[Union[HumanMessage, AIMessage]]:
    lc_messages = []
    for msg in messages:
        role = msg.role
        content_list = msg.content
        text_content = [ c for c in content_list if c.type == "text" ]
        text = " ".join([c.text for c in text_content])

        if role == "user":
            lc_messages.append(HumanMessage(content=text))
        elif role == "assistant":
            lc_messages.append(AIMessage(content=text))
        else:
            pass

    return lc_messages

@router.post('/chat')
async def chat(body: MessagesPayload):
    logger.info(f"Chat request received: {body}")
    messages = convert_frontend_messages_to_langchain(body.messages)
    return StreamingResponse(
        process_chat_message_stream(messages, '123'),
        media_type="text/event-stream"
    )

@router.post("/chat_sync")
def chat_sync(body: MessagesPayload):
    messages = convert_frontend_messages_to_langchain(body.messages)
    return process_chat_message_sync(messages, '123')


## WebSocket
ws_router = APIRouter()

# temp - to remove
async def repeat_every_n_seconds(n, socket: WebSocket):
    while True and socket.client_state == WebSocketState.CONNECTED:
        res = {
            "success": True,
            "data": {
                "channel": "general",
                "message": "Hello from the server!"
            }
        }
        await socket.send_text(json.dumps(res))
        await asyncio.sleep(n)

@ws_router.websocket("/chat/{thread_id}")
async def chat_ws(websocket: WebSocket, thread_id: str):
    await websocket.accept()
    # background_task = asyncio.create_task(repeat_every_n_seconds(3, websocket))
    
    # try:
    #     while True:
    #         data = await websocket.receive_text()
    #         data = json.loads(data)
    #         message = data.get("message")
    #         res = {
    #             "success": True,
    #             "data": {
    #                 "channel": "general",
    #                 "message": message
    #             }
    #             }
    #         await websocket.send_text(json.dumps(res))
    # except Exception as e:
    #     logger.error(f"Error in chat_ws: {e}")
    #     background_task.cancel()

import asyncio
import json
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from bots._openai import OpenAIClient

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_json(self, websocket: WebSocket, data: dict):
        await websocket.send_json(data)


manager = ConnectionManager()


@app.websocket("/openai/ws/completion")
async def websocket_completion(websocket: WebSocket):
    await manager.connect(websocket)
    openai_client = OpenAIClient()
    try:
        while True:
            data = await websocket.receive_json()
            prompt = data.get("prompt")
            stream_res = openai_client.completion(prompt, stream=True)

            for r in stream_res:
                await manager.send_json(websocket, r)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/openai/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await manager.connect(websocket)
    openai_client = OpenAIClient()
    try:
        while True:
            data = await websocket.receive_json()
            messages = data.get("messages")
            stream_res = openai_client.chat_completion(messages, stream=True)

            for r in stream_res:
                await manager.send_json(websocket, r)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("websocket_server:app", host="0.0.0.0", port=8001)

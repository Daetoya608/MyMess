from typing import Annotated, Dict
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from chat import decode_jwt
from data_transform import get_token_data_from_websocket
from schemas import MessageBase

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket):
        user_data = get_token_data_from_websocket(websocket)
        if user_data is None:
            return
        await websocket.accept()
        self.active_connections[user_data["id"]] = websocket

    async def disconnect(self, websocket: WebSocket):
        user_data = get_token_data_from_websocket(websocket)
        if user_data is None:
            return
        self.active_connections.pop(user_data["id"], "websocket not in base")

    async def send_message(self, websocket: WebSocket, message: MessageBase):
        await websocket.send_json(message.model_dump())


manager = ConnectionManager()

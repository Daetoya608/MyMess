import json
import asyncio
from typing import Annotated, Dict
from fastapi import WebSocket, WebSocketDisconnect, APIRouter, WebSocketException
from chat import decode_jwt
from data_transform import get_token_data_from_websocket, get_message_from_token
from schemas import MessageBase
from models import add_content_and_message
from chat_redis import (
    get_part_user_messages,
    delete_part_user_messages,
    store_message
)


async def send_json_message(websocket: WebSocket, json_data: str) -> bool:
    await websocket.send_json(json_data)  # отправляем данные клиенту
    try:
        ack = await asyncio.wait_for(websocket.receive_text(), timeout=5)
        if ack == "received":
            print("Сообщения доставлены")
            return True
    except asyncio.TimeoutError:
        print("Клиент не подтвердил получение")
    return False


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.receive_flags: Dict[int, bool]

    async def connect(self, websocket: WebSocket):
        user_data = get_token_data_from_websocket(websocket)
        if user_data is None:
            await websocket.close()
            return
        await websocket.accept()
        self.active_connections[user_data["id"]] = websocket

    async def disconnect(self, websocket: WebSocket):
        user_data = get_token_data_from_websocket(websocket)
        if user_data is None:
            return
        if self.active_connections.get(user_data["id"]) is None:
            return
        self.active_connections.pop(user_data["id"], "websocket not in base")

    # возвращаем False, если нет новых сообщений
    async def send_new_messages_for_user(self, websocket: WebSocket, user_id: int) -> bool:
        messages_part = await get_part_user_messages(user_id)           # получаем первые n(=20) сообщений из redis
        if len(messages_part) == 0:
            return False
        is_send = await send_json_message(websocket, messages_part)        # отправляем сообщение, получаем подтверждение
        if not is_send:    # если не доставлено заканчиваем
            return True
        await delete_part_user_messages(user_id)            # удаляем из redis
        return True

    async def send_messages_task(self, websocket: WebSocket, user_id: int):
        while True:
            is_send = await self.send_new_messages_for_user(websocket, user_id)
            if not is_send:
                await asyncio.sleep(0.1)
                break

    async def try_send_message_task(self, websocket: WebSocket, user_id: int):
        try:
            await self.send_messages_task(websocket, user_id)
        except WebSocketDisconnect:
            await self.disconnect(websocket)

    # получение и сохранение данных в базу
    # async def get_message(self, websocket: WebSocket):
    #     token = await websocket.receive_text()              # получаем токен
    #     message_data = get_message_from_token(token)     # получаем информацию (dict) из токена
    #     if message_data is None:
    #         print("invalid token")
    #         return
    #     receiver_id = message_data["message"]["receiver_id"]           # получаем индекс получателя
    #     await store_message(receiver_id, json.dumps(message_data["message"]))       # сохраняем в redis
    #     await websocket.send_text("received")          # отправляем подтверждение принятия
    #     await add_content_and_message(message_data["message"])     # сохраняем в postgresql

    async def get_message(self, websocket: WebSocket):
        message_data = await websocket.receive_json()
        await store_message(message_data["receiver_id"], json.dumps(message_data))
        await websocket.send_text("received")
        # await add_content_and_message(message_data)

    async def get_message_task(self, websocket: WebSocket):
        while True:
            await self.get_message(websocket)

    async def try_get_message_task(self, websocket: WebSocket):
        try:
            await self.get_message_task(websocket)
        except WebSocketDisconnect:
            await self.disconnect(websocket)

    # async def confirm(self, websocket: WebSocket):


    async def receive_data(self, websocket: WebSocket, queue: asyncio.Queue):
        data: dict = await websocket.receive_json()
        if data and (data["type"] in ("message", "received")):
            return data
        return None



manager = ConnectionManager()





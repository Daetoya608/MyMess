import json
import asyncio
import time
from typing import Annotated, Dict
from fastapi import WebSocket, WebSocketDisconnect, APIRouter, WebSocketException
from chat import decode_jwt
from data_transform import get_token_data_from_websocket, get_message_from_token
from schemas import MessageBase
from models import add_message, add_message_by_obj
from chat_redis import (
    get_part_chat_messages,
    delete_part_chat_messages,
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


async def send_receive(websocket: WebSocket):
    answer = {
        "type": "received"
    }
    await websocket.send_json(json.dumps(answer))

def default_answer(time_key):
    answer: dict = {
        "type": "ack",
        "time_key": time_key
    }
    return answer


class ConnectionManager:
    def __init__(self,user_id: int, websocket: WebSocket, to_delete_queue: asyncio.Queue):
        self.user_id = user_id
        self.websocket = websocket
        self.to_delete_queue = to_delete_queue
        self.ack_queue = asyncio.Queue()
        self.messages_queue = asyncio.Queue()

    async def disconnect(self):
        await self.to_delete_queue.put(self)

    async def send_data(self, data: dict):
        await self.websocket.send_json(json.dumps(data))

    async def receive_expectation(self, time_key: int, timeout = 5):
        try:
            ack = await asyncio.wait_for(self.ack_queue.get(), timeout=timeout)
            if ack["time_key"] == time_key:
                return True
            return False
        except asyncio.TimeoutError:
            return False

    async def send_data_with_ack(self, messages_data: dict):
        max_try_count = 50
        messages_data["time_key"] = time.perf_counter_ns()
        for _ in range(max_try_count):
            await self.send_data(messages_data)
            if await self.receive_expectation(messages_data["time_key"]):
                return

    async def receive_requests(self):
        request_data: dict = await self.websocket.receive_json()
        if request_data.get("type") == "messages":
            await self.messages_queue.put(request_data)
            await self.send_data(default_answer(request_data.get("time_key")))
        elif request_data.get("type") == "ack":
            await self.ack_queue.put(request_data)
        else:
            print("Неверная структура запроса")

    async def get_messages(self):
        try:
            requests_data = await asyncio.wait_for(self.messages_queue.get(), timeout=10)
            messages = requests_data["messages"]
            for message in messages:
                chat_id = message["chat_id"]
                await store_message(chat_id, message)
                await add_message_by_obj(message)
        except TimeoutError:
            return

    async def get_messages_task(self):
        try:
            while True:
                await self.get_messages()
        except WebSocketDisconnect:
            await self.disconnect()


    # возвращаем False, если не получилось отправить
    async def send_new_messages_for_user(self, websocket: WebSocket, user_id: int) -> bool:
        messages_part = await get_part_chat_messages(user_id)           # получаем первые n(=20) сообщений из redis
        if len(messages_part) == 0:
            return True
        is_send = await send_json_message(websocket, messages_part)        # отправляем сообщение, получаем подтверждение
        if not is_send:    # если не доставлено заканчиваем
            return False
        await delete_part_chat_messages(user_id)            # удаляем из redis
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


    # async def get_message(self, websocket: WebSocket):
    #     message_data = await websocket.receive_json()
    #     await store_message(message_data["receiver_id"], json.dumps(message_data))
    #     await websocket.send_text("received")
    #     # await add_content_and_message(message_data)
    #
    # async def get_message_task(self, websocket: WebSocket):
    #     while True:
    #         await self.get_message(websocket)
    #
    # async def try_get_message_task(self, websocket: WebSocket):
    #     try:
    #         await self.get_message_task(websocket)
    #     except WebSocketDisconnect:
    #         await self.disconnect(websocket)

    # async def receive_data(self, websocket: WebSocket, queue: asyncio.Queue):
    #     data: dict = await websocket.receive_json()
    #     if data and (data["type"] in ("message", "received")):
    #         return data
    #     return None


class GlobalConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, ConnectionManager] = {}
        self.to_delete_queue: asyncio.Queue = asyncio.Queue()

    async def new_connection(self, websocket: WebSocket):
        user_data = get_token_data_from_websocket(websocket)
        if user_data is None:
            await websocket.close()
            return
        await websocket.accept()
        self.active_connections[user_data["id"]] = ConnectionManager(websocket, self.to_delete_queue)

    async def delete_disconnected(self):
        while True:
            try:
                disconnected_user: ConnectionManager = await asyncio.wait_for(self.to_delete_queue.get(), timeout=1)
                del self.active_connections[disconnected_user.user_id]
            except TimeoutError:
                continue

    async def 


manager = GlobalConnectionManager()





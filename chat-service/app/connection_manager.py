import json
import asyncio
import time
import math
from typing import Annotated, Dict, List
from fastapi.websockets import WebSocketState
from fastapi import WebSocket, WebSocketDisconnect, APIRouter, WebSocketException
from chat import decode_jwt
from data_transform import get_token_data_from_websocket, get_message_from_token
from schemas import MessageBase
from models import add_message, add_message_by_obj
from chat_redis import (
    get_part_chat_messages,
    delete_part_chat_messages,
    store_message,
    get_all_messages_for_user_id
)


# async def send_json_message(websocket: WebSocket, json_data: str) -> bool:
#     await websocket.send_json(json_data)  # отправляем данные клиенту
#     try:
#         ack = await asyncio.wait_for(websocket.receive_text(), timeout=5)
#         if ack == "received":
#             print("Сообщения доставлены")
#             return True
#     except asyncio.TimeoutError:
#         print("Клиент не подтвердил получение")
#     return False
#
#
# async def send_receive(websocket: WebSocket):
#     answer = {
#         "type": "received"
#     }
#     await websocket.send_json(json.dumps(answer))

def default_answer(time_key):
    answer: dict = {
        "type": "ack",
        "time_key": time_key
    }
    return answer


def default_sending_messages(messages: List[Dict]):
    result: dict = {
        "type": "messages",
        "messages": messages
    }
    return result


def split_messages(messages: List[Dict], num_split: int = 20):
    begin_list = lambda x: num_split * x
    end_list = lambda x: num_split * x if num_split * x < len(messages) else len(messages)
    return [messages[begin_list(i):end_list(i + 1)] for i in range(math.ceil(len(messages)/num_split))]


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
            await self.ack_queue.put(ack)
            return False
        except asyncio.TimeoutError:
            return False

    async def send_data_with_ack(self, messages_data: dict):
        max_try_count = 50
        messages_data["time_key"] = time.perf_counter_ns()
        for _ in range(max_try_count):
            await self.send_data(messages_data)
            if await self.receive_expectation(messages_data["time_key"]):
                return True
        return False

    async def receive_requests(self):
        try:
            if self.websocket.client_state != WebSocketState.CONNECTED:
                print("receive_requets - disconnect")
                raise WebSocketDisconnect
            print("Ждем данных от клиента")
            request_data: dict = await self.websocket.receive_json()
            # request_data: dict = await asyncio.wait_for(self.websocket.receive_json(), timeout=3)
            print(f"Данные от клиента {type(request_data)}: {request_data}")
            if request_data.get("type") == "messages":
                print("TYPE == MESSAGES")
                await self.messages_queue.put(request_data)
                print("send data here")
                await self.send_data(default_answer(request_data.get("time_key")))
            elif request_data.get("type") == "ack":
                await self.ack_queue.put(request_data)
            else:
                print("Неверная структура запроса")
        except asyncio.TimeoutError:
            print("Ошибка: долгое ожидание")


    async def receive_requests_task(self):
        while self.websocket.client_state == WebSocketState.CONNECTED:
            try:
                print("receive_requests_task-1")
                await self.receive_requests()
            except WebSocketDisconnect:
                await self.disconnect()
                print("receive_requests_task - WebSocketDisconnect")
                break
                # return False
            except Exception as e:
                print(f"receive_requests_task - Exception: {e}")
                await self.disconnect()
                break
                # return False
            finally:
                await self.disconnect()


    async def get_messages(self):
        try:
            # requests_data = await asyncio.wait_for(self.messages_queue.get(), timeout=10)
            requests_data = await self.messages_queue.get()
            print(f"!!!!!! requests_data = {requests_data}")
            messages = requests_data.get("messages")
            if messages is None:
                print("Ошибка: get_messages -> messages == None")
            for message in messages:
                chat_id = message["chat_id"]
                print(f"сохранено {message}")
                await store_message(chat_id, json.dumps(message))
                #await add_message_by_obj(message)
        except asyncio.TimeoutError:
            print("timeout error")
            return

    async def get_messages_task(self):
        print("enter get_messages_task")
        while self.websocket.client_state == WebSocketState.CONNECTED:
            print("get_message_task-117")
            try:
                await self.get_messages()
            except WebSocketDisconnect:
                print("get_messages_task-121")
                await self.disconnect()
                break
            except Exception as e:
                print(f"Error get_messages_task: {e}")
                await self.disconnect()
                break


    async def send_messages(self, messages: List[Dict]):
        messages_data = default_sending_messages(messages)
        is_send = await self.send_data_with_ack(messages_data)
        if is_send:
            return
        # put back
        for message in messages:
            await store_message(message["chat_id"], json.dumps(message))

    async def send_all_messages_by_chunks(self):
        print("send_all_messages_by_chunks_{begins}")
        messages = await get_all_messages_for_user_id(self.user_id)
        # print(messages)
        messages_chunks = split_messages(messages)
        print(f"messages_chunks: {messages_chunks}")
        for messages_chunk in messages_chunks:
            # print(f"messages_chunk: {messages_chunk}")
            await self.send_messages(messages_chunk)

    async def send_messages_task(self):
        while self.websocket.client_state == WebSocketState.CONNECTED:
            try:
                await self.send_all_messages_by_chunks()
                await asyncio.sleep(3)
            except WebSocketDisconnect:
                print("send_messages_task - WebSocketDisconnect")
                await self.disconnect()
                break
            except Exception as e:
                print(f"send_messages_task - Exception: {e}")
                await self.disconnect()
                break



    # async def send_new_messages_for_user(self, websocket: WebSocket, user_id: int) -> bool:
    #     messages_part = await get_part_chat_messages(user_id)           # получаем первые n(=20) сообщений из redis
    #     if len(messages_part) == 0:
    #         return True
    #     is_send = await send_json_message(websocket, messages_part)        # отправляем сообщение, получаем подтверждение
    #     if not is_send:    # если не доставлено заканчиваем
    #         return False
    #     await delete_part_chat_messages(user_id)            # удаляем из redis
    #     return True
    #
    # async def send_messages_task(self, websocket: WebSocket, user_id: int):
    #     while True:
    #         is_send = await self.send_new_messages_for_user(websocket, user_id)
    #         if not is_send:
    #             await asyncio.sleep(0.1)
    #             break
    #
    # async def try_send_message_task(self, websocket: WebSocket, user_id: int):
    #     try:
    #         await self.send_messages_task(websocket, user_id)
    #     except WebSocketDisconnect:
    #         await self.disconnect(websocket)

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
        self.to_activate_connection: asyncio.Queue = asyncio.Queue()
        self.users_tasks: Dict[int, List[asyncio.Task]] = {}

    async def new_connection(self, websocket: WebSocket):
        user_data = get_token_data_from_websocket(websocket)
        if user_data is None:
            await websocket.close()
            return None
        await websocket.accept()
        connection_manager = ConnectionManager(user_data["id"], websocket, self.to_delete_queue)
        self.active_connections[user_data["id"]] = connection_manager
        await self.to_activate_connection.put(connection_manager)
        print(f"connection_manager: {connection_manager.user_id}")
        return connection_manager

    async def delete_disconnected(self):
        while True:
            print("delete_disconnected - {begins}")
            try:
                disconnected_user: ConnectionManager = await asyncio.wait_for(self.to_delete_queue.get(), timeout=10)
                del self.active_connections[disconnected_user.user_id]
                for task in self.users_tasks[disconnected_user.user_id]:
                    task.cancel()
            except asyncio.TimeoutError:
                continue

    async def start_task(self):
        while True:
            try:
                connection_manager: ConnectionManager = await asyncio.wait_for(
                    self.to_activate_connection.get(),
                    timeout=3
                )
                # asyncio.create_task(connection_manager.receive_requests_task())
                # asyncio.create_task(connection_manager.get_messages_task())
            except WebSocketDisconnect:
                print("start_task_225")
                break
            except asyncio.TimeoutError:
                continue



global_connection_manager = GlobalConnectionManager()
# task1 = asyncio.create_task(global_connection_manager.start_task())
task2 = asyncio.create_task(global_connection_manager.delete_disconnected())



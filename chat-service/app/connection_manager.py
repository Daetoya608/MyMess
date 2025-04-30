import json
import asyncio
import time
import math
from typing import Dict, List
from fastapi.websockets import WebSocketState
from fastapi import WebSocket, WebSocketDisconnect
from data_transform import get_token_data_from_websocket
from models import  add_message_by_obj, get_chat_by_chat_id
from commands_handlers import command_handler
from serviceRequests import get_users_info
from chat_redis import (
    store_message,
    get_and_delete_all_user_messages,
    get_and_delete_all_new_chats,
    get_users_by_chat_id
)


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


def default_sending_chat(chat_id: int, chat_name: str, members: List[int]):
    result: dict = {
        "type": "operations",
        "operations": [
            {
                "operation": "new_chat",
                "chat_id": chat_id,
                "chat_name": chat_name,
                "members": members
            }
        ]
    }
    return result


def default_users_info(users_info: List[Dict]):
    result: dict = {
        "type": "users_info",
        "users_info": users_info
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
        # self.ack_queue = asyncio.Queue()
        self.getting_messages_queue = asyncio.Queue()
        self.sending_messages_queue = asyncio.Queue()
        self.commands_queue = asyncio.Queue()
        self.ack_set = set()

    # добавить очередь для отправки информации

    async def disconnect(self):
        await self.to_delete_queue.put(self)


    async def wait_key(self, key):
        while key not in self.ack_set:
            await asyncio.sleep(0.03)
        return True


    async def send_data(self, data: dict):
        await self.websocket.send_json(json.dumps(data))


    # async def receive_expectation(self, time_key: int, timeout = 5):
    #     try:
    #         ack = await asyncio.wait_for(self.ack_queue.get(), timeout=timeout)
    #         print(f"time_key={time_key} --- ack[\"time_key\"]={ack["time_key"]}\n")
    #         if ack["time_key"] == time_key:
    #             return True
    #         await self.ack_queue.put(ack)
    #         return False
    #     except asyncio.TimeoutError:
    #         return False


    async def receive_expectation(self, time_key: int, timeout = 5):
        try:
            ack = await asyncio.wait_for(self.wait_key(time_key), timeout=timeout)
            return ack
        except asyncio.TimeoutError:
            return False


    async def send_data_with_ack(self, messages_data: dict):
        max_try_count = 50
        time_key = time.perf_counter_ns()
        print(f"messages: {messages_data},\ntime_key: {time_key}\n")
        messages_data["time_key"] = time_key
        for _ in range(max_try_count):
            print(f"counter: {_}")
            await self.send_data(messages_data)
            if await self.receive_expectation(time_key):
                return True
        return False


    async def receive_requests(self):
        try:
            if self.websocket.client_state != WebSocketState.CONNECTED:
                # print("receive_requets - disconnect")
                raise WebSocketDisconnect
            print("Ждем данных от клиента")
            request_data: dict = await self.websocket.receive_json()
            # request_data: dict = await asyncio.wait_for(self.websocket.receive_json(), timeout=3)
            print(f"Данные от клиента {type(request_data)}: {request_data}")
            if request_data.get("type") == "messages":
                print("TYPE == MESSAGES")
                await self.getting_messages_queue.put(request_data)
                print("send data here")
                await self.send_data(default_answer(request_data.get("time_key")))
            elif request_data.get("type") == "ack":
                print(f"ack = {request_data}")
                # await self.ack_queue.put(request_data)
                self.ack_set.add(request_data["time_key"])
            elif request_data.get("type") == "commands":
                print(f"commands = {request_data}")
                await self.commands_queue.put(request_data)
                await self.send_data(default_answer(request_data.get("time_key")))
            else:
                print("Неверная структура запроса")
        except asyncio.TimeoutError:
            print("Ошибка: долгое ожидание")


    async def receive_requests_task(self):
        while self.websocket.client_state == WebSocketState.CONNECTED:
            try:
                # print("receive_requests_task-1")
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


    async def sending_messages_from_queue(self):
        print("sending_messages_from_queue")
        new_message = await self.sending_messages_queue.get()
        is_send = await self.send_data_with_ack(new_message)
        print("Sended")
        if is_send:
            return True
        # put back
        await self.sending_messages_queue.put(new_message)
        return False


    async def sending_messages_from_queue_task(self):
        while self.websocket.client_state == WebSocketState.CONNECTED:
            try:
                await self.sending_messages_from_queue()
            except WebSocketDisconnect:
                print(f"sending_messages_from_queue_task - WebSocketDisconnect")
                await self.disconnect()
                break
            except Exception as e:
                print(f"sending_messages_from_queue_task - Exception: {e}")
                await self.disconnect()
                break


    async def get_messages(self):
        try:
            # requests_data = await asyncio.wait_for(self.messages_queue.get(), timeout=10)
            requests_data = await self.getting_messages_queue.get()
            # print(f"!!!!!! requests_data = {requests_data}")
            messages = requests_data.get("messages")
            if messages is None:
                print("Ошибка: get_messages -> messages == None")
            for message in messages:
                message["sender_id"] = self.user_id
                chat_id = message["chat_id"]
                # print(f"тип chat_id = {type(chat_id)}, chat_id = {chat_id}")
                # print(f"сохранено {message}")
                added_message = await add_message_by_obj(message)
                if added_message:
                    message["id"] = added_message.id
                    await store_message(chat_id, json.dumps(message))
        except asyncio.TimeoutError:
            print("timeout error")
            return


    async def get_messages_task(self):
        print("enter get_messages_task")
        while self.websocket.client_state == WebSocketState.CONNECTED:
            # print("get_message_task - {cycle-begin}")
            try:
                await self.get_messages()
            except WebSocketDisconnect:
                print("get_messages_task - WebSocketDisconnect")
                await self.disconnect()
                break
            except Exception as e:
                print(f"get_messages_task: Exception - {e}")
                await self.disconnect()
                break


    async def save_users_info(self, members: List[int]):
        print("save_users_info - begin")
        data_response = await get_users_info(members)
        if not data_response["status"]:
            print(f"\nsave_users_info - data_response if False\n")
            return None
        data_list = data_response["users_data"]
        print(f"save_users_info = {data_list}")
        users_info_data = default_users_info(data_list)
        await self.sending_messages_queue.put(users_info_data)
        print("save_users_info - end")


    async def save_new_chats_to_queue(self, chat_id):
        print(f"\nsave_new_chats_to_queue - begin")
        members_connects = await get_users_by_chat_id(chat_id)
        members = [members_connect.user_id for members_connect in members_connects]
        chat = await get_chat_by_chat_id(chat_id)
        new_chat_operation = default_sending_chat(chat_id, chat.chat_name, members)
        await self.save_users_info(members)
        await self.sending_messages_queue.put(new_chat_operation)
        print(f"save_new_chats_to_queue - end,\nnew_chat={new_chat_operation}")


    async def save_new_chats_by_one(self):
        chats = await get_and_delete_all_new_chats(self.user_id)
        for chat_id in chats:
            await self.save_new_chats_to_queue(chat_id)


    async def save_new_chats_task(self):
        while self.websocket.client_state == WebSocketState.CONNECTED:
            try:
                await self.save_new_chats_by_one()
            except WebSocketDisconnect:
                print(f"save_new_chats_task - WebSocketDisconnect")
                await self.disconnect()
                break
            except Exception as e:
                print(f"save_new_chats_task - Exception: {e}")
                await self.disconnect()
                break


    async def save_messages_to_queue(self, messages: List[Dict]):
        print(f"Messages: {messages}")
        messages_data = default_sending_messages(messages)
        # is_send = await self.send_data_with_ack(messages_data)
        # if is_send:
        #     return True
        await self.sending_messages_queue.put(messages_data)
        # put back
        # for message in messages:
        #     await store_message(message["chat_id"], json.dumps(message))
        # return False


    async def save_all_messages_by_chunks(self):
        # print("send_all_messages_by_chunks_{begins}")
        messages = await get_and_delete_all_user_messages(self.user_id)
        messages_chunks = split_messages(messages)
        if len(messages_chunks) > 0:
            print(f"\nmessages_chunks: {messages_chunks}")
        if len(messages_chunks) == 0:
            return False
        for messages_chunk in messages_chunks:
            await self.save_messages_to_queue(messages_chunk)
        return True


    async def save_messages_in_queue_task(self):
        while self.websocket.client_state == WebSocketState.CONNECTED:
            try:
                await self.save_all_messages_by_chunks()
                await asyncio.sleep(0.03)
            except WebSocketDisconnect:
                print("send_messages_task - WebSocketDisconnect")
                await self.disconnect()
                break
            except Exception as e:
                print(f"send_messages_task - Exception: {e}")
                await self.disconnect()
                break


    async def execute_command(self):
        command_response = await self.commands_queue.get()
        for command in command_response["commands"]:
            result = await command_handler(command)
            if not result["status"]:
                print(result)


    async def execute_command_task(self):
        while self.websocket.client_state == WebSocketState.CONNECTED:
            try:
                await self.execute_command()
                await asyncio.sleep(0.03)
            except WebSocketDisconnect:
                print("execute_command_task - WebSocketDisconnect")
                await self.disconnect()
                break
            except Exception as e:
                print(f"execute_command_task - Exception: {e}")
                await self.disconnect()
                break



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
                print("start_task - WebSocketDisconnect")
                break
            except asyncio.TimeoutError:
                continue




global_connection_manager = GlobalConnectionManager()
# task1 = asyncio.create_task(global_connection_manager.start_task())
# task2 = asyncio.create_task(global_connection_manager.delete_disconnected())



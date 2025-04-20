import asyncio
import websockets
import json
from typing import List, Dict
from scripts import create_messages, default_answer, create_chat, default_func, async_default_func
from client_settings import ClientSettings
from client_chats import ClientChats
from client_handlers import operation_handler, user_info_handler

class Client:

    def __init__(self, client_settings: ClientSettings):
        self.getting_messages_queue = asyncio.Queue()
        self.sending_messages_queue = asyncio.Queue()
        self.getting_operation_queue = asyncio.Queue()
        self.getting_users_info_queue = asyncio.Queue()
        self.ack_queue = asyncio.Queue()
        # self.result_list: List = []
        self.settings: ClientSettings = client_settings
        self.chats: ClientChats = ClientChats()
        self.get_message_handler_func = default_func
        self.async_get_message_handler_func = async_default_func


    async def send_ask(self, websocket: websockets.ClientConnection, time_key: int):
        try:
            requests_data = {
                "type": "ack",
                "time_key": time_key
            }
            requests_data_json = json.dumps(requests_data)
            await websocket.send(requests_data_json)
        except Exception as e:
            print(f"send_ask - Exception: {e}")


    async def send_data(self, websocket: websockets.ClientConnection, data: dict):
        await websocket.send(json.dumps(data))


    async def add_to_sending_messages_queue(self, messages: Dict):
        """
        Добавляет messages в очередь сообщений, ожидающих отправки

        :param messages:
        {
            "type":= "messages",
            "time_key":= int,
            "messages": [
                {
                    "chat_id": int,
                    "content_text": str
                }
            ]
        }
        :return:
        """
        await self.sending_messages_queue.put(messages)


    async def receiver_handler(self, websocket: websockets.ClientConnection):
        request_str: str = await websocket.recv()
        request_data: dict = json.loads(json.loads(request_str))
        print(f"receiver_handler - begin, \nrequest_data={request_data}")
        if request_data.get("type") == "messages":
            await self.getting_messages_queue.put(request_data)
            await self.send_data(websocket, default_answer(request_data.get("time_key")))
            await asyncio.sleep(0.1)
        elif request_data.get("type") == "ack":
            await self.ack_queue.put(request_data)
        elif request_data.get("type") == "operations":
            await self.getting_operation_queue.put(request_data)
            await self.send_data(websocket, default_answer(request_data.get("time_key")))
            await asyncio.sleep(0.1)
        elif request_data.get("type") == "users_info":
            print(f"\nrequest_data.get == users_info")
            await self.getting_users_info_queue.put(request_data)
            await self.send_data(websocket, default_answer(request_data.get("time_key")))
            await asyncio.sleep(0.1)
        else:
            print("Неверная структура данных")


    async def receiver_handler_task(self, websocket: websockets.ClientConnection):
        while True:
            try:
                await self.receiver_handler(websocket)
            except Exception as e:
                print(f"receiver_handler_task - Exception: {e}")
                continue


    async def get_message(self, websocket: websockets.ClientConnection):
        data: dict = await self.getting_messages_queue.get()
        # self.result_list.append(data)
        self.get_message_handler_func(data)
        await self.async_get_message_handler_func(data)
        print(f"\ndata-get_message: {data}\n")
        await self.send_ask(websocket, int(data["time_key"]))
        await asyncio.sleep(0.1)


    async def get_message_task(self, websocket: websockets.ClientConnection):
        while True:
            try:
                await self.get_message(websocket)
            except Exception as e:
                print(f"get_message_task - Exception: {e}")
                continue


    async def send_message(self, websocket: websockets.ClientConnection):
        # message = await asyncio.to_thread(input)  # input("Write message: ")
        #
        # if message == "result":
        #     print(f"COUNT: {len(self.result_list)}\n\ndata={self.result_list}")
        #     return True

        # await websocket.send(json.dumps(create_messages(message, chat_id)))

        messages = await self.sending_messages_queue.get()
        await websocket.send(json.dumps(messages))

        print("Отправлено")
        response = await self.ack_queue.get()
        # print(f"Получено от сервера, ack: {response}")
        await asyncio.sleep(0.1)


    async def send_message_task(self, websocket: websockets.ClientConnection):
        while True:
            try:
                await self.send_message(websocket)
            except Exception as e:
                print(f"send_message_task - Exception: {e}")


    async def update_users_info(self):
        data_response = await self.getting_users_info_queue.get()
        print(f"\nupdate_users_info. data_response={data_response}")
        for user_info in data_response["users_info"]:
            result = await user_info_handler(user_info)
            if result is None:
                print("update_users_info - result is None")


    async def update_users_info_task(self):
        while True:
            try:
                await self.update_users_info()
            except Exception as e:
                print(f"\nupdate_users_info_task - Exception: {e}")


    async def server_request_create_chat(self, chat_name: str, members: List[int]):
        await self.sending_messages_queue.put(create_chat(chat_name, members))


    async def execute_operation(self):
        operation_response = await self.getting_operation_queue.get()
        print(f"execute_operation - begin. operation_response={operation_response}")
        for operation in operation_response["operations"]:
            print(f"\noperation={operation}")
            result = await operation_handler(operation)
            if result is None:
                print("execute_operation - exception")


    async def execute_operation_task(self):
        while True:
            try:
                await self.execute_operation()
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"execute_operation_task - Exception: {e}")


    async def websocket_client(self, domain = "127.0.0.1:8003"):
        uri = f"ws://{domain}/ws"  # адрес твоего сервера

        async with websockets.connect(uri, additional_headers={"token": self.settings.token}) as websocket:
            task1 = asyncio.create_task(self.receiver_handler_task(websocket))
            task2 = asyncio.create_task(self.get_message_task(websocket))
            task3 = asyncio.create_task(self.send_message_task(websocket))
            task4 = asyncio.create_task(self.execute_operation_task())

            await task1
            await task2
            await task3
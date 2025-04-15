import asyncio
import websockets
import json
from typing import List
from scripts import create_messages, default_answer
from client_settings import ClientSettings

class Client:

    def __init__(self, client_settings: ClientSettings):
        self.messages_queue = asyncio.Queue()
        self.ack_queue = asyncio.Queue()
        self.result_list: List = []
        self.settings: ClientSettings = client_settings


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


    async def receiver_handler(self, websocket: websockets.ClientConnection):
        request_str: str = await websocket.recv()
        request_data: dict = json.loads(json.loads(request_str))
        if request_data.get("type") == "messages":
            await self.messages_queue.put(request_data)
            await self.send_data(websocket, default_answer(request_data.get("time_key")))
            print(request_data)
            await asyncio.sleep(0.1)
        elif request_data.get("type") == "ack":
            await self.ack_queue.put(request_data)
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
        data: dict = await self.messages_queue.get()
        self.result_list.append(data)
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


    async def send_message(self, websocket: websockets.ClientConnection, chat_id: int):
        message = await asyncio.to_thread(input)  # input("Write message: ")

        if message == "result":
            print(f"COUNT: {len(self.result_list)}\n\ndata={self.result_list}")
            return True

        await websocket.send(json.dumps(create_messages(message, chat_id)))
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
                continue


    async def websocket_client(self, domain = "127.0.0.1:8003"):
        uri = f"ws://{domain}/ws"  # адрес твоего сервера

        async with websockets.connect(uri, additional_headers={"token": self.settings.token}) as websocket:
            task1 = asyncio.create_task(self.receiver_handler_task(websocket))
            task2 = asyncio.create_task(self.get_message_task(websocket))
            task3 = asyncio.create_task(self.send_message_task(websocket))

            await task1
            await task2
            await task3



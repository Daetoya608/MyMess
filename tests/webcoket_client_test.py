import asyncio
import websockets
import json
import time

def create_messages(text_message: str, sender_id: int, chat_id: int):
    request_data = {
        "type": "messages",
        "time_key": time.perf_counter_ns(),
        "messages": [
            {
                "sender_id": sender_id,
                "chat_id": chat_id,
                "content_text": text_message
            },
        ]
    }
    return request_data


async def send_ask(websocket: websockets.ClientConnection, time_key: int):
    requests_data = {
        "type": "ack",
        "time_key": time_key
    }
    await websocket.send(json.dumps(requests_data))


async def get_mode(uri, token):
    async with websockets.connect(uri, additional_headers={"token": token}) as websocket:
        while True:
            response_data = await websocket.recv()
            response_data_dict = json.loads(response_data)
            data = json.loads(response_data_dict)
            print(f"ТИП - {type(data)}")
            print(data)
            print(type(data["time_key"]))
            await send_ask(websocket, int(data["time_key"]))
            await asyncio.sleep(5)


async def send_mode(uri, token):
    async with websockets.connect(uri, additional_headers={"token": token}) as websocket:
        while True:
            message = await asyncio.to_thread(input, "Введи сообщение") #input("Write message: ")
            await websocket.send(json.dumps(create_messages(message, 1, 1)))
            print("Отправлено")
            response = await websocket.recv()
            print(f"Получено от сервера: {response}")
            await asyncio.sleep(5)


async def websocket_client():
    uri = "ws://localhost:8000/ws"  # адрес твоего сервера
    token = input("Введите токен: ")

    mode = input("send/get: ")
    if mode == "send":
        await send_mode(uri, token)
    elif mode == "get":
        await get_mode(uri, token)


asyncio.run(websocket_client())

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

async def send_ask(websocket: websockets.ClientConnection, time_key: int):
    requests_data = {
        "type": "ack",
        "time_key": time_key
    }
    await websocket.send(json.dumps(requests_data))


async def websocket_client():
    uri = "ws://localhost:8000/ws"  # адрес твоего сервера
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NSwidXNlcm5hbWUiOiJmb3JleGFtcGxlIiwiZXhwIjoxNzQzODc2ODkxfQ.AY7O8xiQ_mbP4wOksQJZAvs90d4lOVjHjZTA6Z0kyiE"
    async with websockets.connect(uri, additional_headers={"token": token}) as websocket:
        # Пример данных
        # print(json.dumps(create_messages("Hello bro", 1, 1)))

        while True:
            response_data = await websocket.recv()
            response_data = json.loads(response_data)
            print(response_data)
            await send_ask(websocket, response_data["time_key"])
            await asyncio.sleep(5)

            # await websocket.send(json.dumps(create_messages("hello bro", 1, 1)))
            # print("Отправлено")
            # response = await websocket.recv()
            # print(f"Получено от сервера: {response}")
            # await asyncio.sleep(5)


asyncio.run(websocket_client())

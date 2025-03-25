import asyncio
import json
import websockets
from websockets import ClientConnection

headers = {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NSwidXNlcm5hbWUiOiJmb3JleGFtcGxlIiwiZXhwIjoxNzQyOTIzNjQ4fQ.lHps8RkhvzeGpaTAtRO3uoyFanR0kfFAngG50gPf-Ig",
}
send_data = {
    "sender_id": 1,
    "receiver_id": 2,
    "content": {
        "text_content": "HELLO WORLD"
    }
}
def send_func(text: str):
    return {
        "sender_id": 1,
        "receiver_id": 2,
        "content": {
            "text_content": text
        }
    }

async def client():
    uri = "ws://localhost:8000/ws"  # Адрес WebSocket-сервера
    async with websockets.connect(uri, additional_headers=headers) as websocket:
        # Запуск двух асинхронных задач
        await send_messages(websocket)

async def send_messages(websocket):
    """Функция для отправки сообщений серверу"""
    try:
        while True:
            user_data = input("Введите сообщение: ")
            await websocket.send(json.dumps(send_func(user_data)))  # Отправляем сообщение серверу
            try:
                ack = await asyncio.wait_for(websocket.recv(), timeout=5)
                if ack == "received":
                    print("Сообщения доставлены")
                    # return True
            except asyncio.TimeoutError:
                print("Клиент не подтвердил получение")
    except Exception as e:
        print(f"Ошибка: {e}")

async def get_messages(websocket: ClientConnection):
    """Функция для получения сообщений от сервера"""
    try:
        while True:
            message = await websocket.recv()
            await websocket.send("received")
            print(f"Новое сообщение: {message}")
    except Exception as e:
        print(f"Ошибка: {e}")


# Запуск клиента
asyncio.run(client())

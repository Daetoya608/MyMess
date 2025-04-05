import asyncio
import websockets
import json
import time

async def websocket_client():
    uri = "ws://localhost:8000/ws"  # адрес твоего сервера
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NSwidXNlcm5hbWUiOiJmb3JleGFtcGxlIiwiZXhwIjoxNzQzODc2ODkxfQ.AY7O8xiQ_mbP4wOksQJZAvs90d4lOVjHjZTA6Z0kyiE"
    async with websockets.connect(uri, additional_headers={"token": token}) as websocket:
        # Пример данных
        request_data = {
            "type": "messages",
            "time_key": time.perf_counter_ns(),
            "messages": [
                {
                    "sender_id": 1,
                    "chat_id": 1,
                    "content_text": "hello world"
                },
                {
                    "sender_id": 1,
                    "chat_id": 1,
                    "content_text": "second message"
                }
            ]
        }

        print(json.dumps(request_data))
        print(1)

        while True:
            await websocket.send(json.dumps(request_data))
            print("Отправлено")
            response = await websocket.recv()
            print(f"Получено от сервера: {response}")
            await asyncio.sleep(5)

        print(2)
        response = await websocket.recv()
        print(3)
        print(f"Получено от сервера: {response}")
        # Можно продолжить цикл или завершить соединение
        print("Закрытие соединения")
        counter = 0
        while True:
            counter += 1
            print(counter)
            await asyncio.sleep(100)

asyncio.run(websocket_client())

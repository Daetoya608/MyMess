import json

from fastapi import APIRouter, WebSocket, FastAPI, WebSocketDisconnect
import asyncio
import hashlib
from connection_manager import global_connection_manager
from data_transform import get_token_data_from_websocket

from chat_redis import redis_client
# socket_router = APIRouter()

app = FastAPI()    # удалить потом

def create_message(chat_id: int, sender_id: int, content_text: str):
    dict_res = {
        "sender_id": sender_id,
        "chat_id": chat_id,
        "content_text": content_text
    }
    return dict_res


# @app.on_event("startup")
# async def startup():
#     for i in range(1, 4):
#         await redis_client.rpush("chat:1", json.dumps(create_message(1, 1, f"message1_{i}")))
#     for i in range(1, 4):
#         await redis_client.rpush("chat:1", json.dumps(create_message(1, 2, f"message2_{i}")))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        print("Приняли соединение")
        con_man = await global_connection_manager.new_connection(websocket)
        # После добавления в очередь `to_activate_connection`,
        # задачи будут автоматически запущены внутри start_task()
        task1 = asyncio.create_task(con_man.receive_requests_task())
        task2 = asyncio.create_task(con_man.get_messages_task())
        # task3 = asyncio.create_task(con_man.send_messages_task())

        # global_connection_manager.users_tasks[con_man.user_id].append(task1)
        # global_connection_manager.users_tasks[con_man.user_id].append(task3)

        await task1
        await task2
        # await task3
    except WebSocketDisconnect:
        print("Пользователь отключился")
    except Exception as e:
        print(f"Ошибка в WebSocket endpoint: {e}")
        await websocket.close()


# # Функция для вычисления SHA-256 хеша файла
# def calculate_file_hash(filename):
#     sha256 = hashlib.sha256()
#     with open(filename, "rb") as file:
#         while chunk := file.read(4096):
#             sha256.update(chunk)
#     return sha256.hexdigest()

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()  # Принимаем соединение
#     while True:
#         data = await websocket.receive_text()  # Ждем команду от клиента
#         if data.startswith("send_file"):
#             # _, filename = data.split(" ", 1)
#             filename = "/home/daetoya/files/example_test.txt"
#             try:
#                 # Вычисляем хеш файла и отправляем его клиенту
#                 file_hash = calculate_file_hash(filename)
#                 await websocket.send_text(f"hash:{file_hash}")
#
#                 # Отправляем сам файл чанками
#                 chunk_size = 4096  # 4 KB
#                 with open(filename, "rb") as file:
#                     while chunk := file.read(chunk_size):
#                         await websocket.send_bytes(chunk)
#                         await asyncio.sleep(0.01)  # Небольшая задержка для плавности
#                 await websocket.send_text("done")  # Сообщаем о завершении
#             except FileNotFoundError:
#                 await websocket.send_text("error: file not found")

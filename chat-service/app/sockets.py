from fastapi import APIRouter, WebSocket, FastAPI
import asyncio
import hashlib
from connection_manager import manager
from data_transform import get_token_data_from_websocket

# socket_router = APIRouter()

app = FastAPI()

# Функция для вычисления SHA-256 хеша файла
def calculate_file_hash(filename):
    sha256 = hashlib.sha256()
    with open(filename, "rb") as file:
        while chunk := file.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()


@app.websocket("/ws")
async def send_message(websocket: WebSocket):
    token_data = get_token_data_from_websocket(websocket)
    if token_data is None:
        print("invalid token")
        await websocket.close()
        return
    user_id = token_data["id"]
    await manager.connect(websocket)
    await manager.try_get_message_task(websocket)
    # send_task = asyncio.create_task(manager.try_send_message_task(websocket, user_id))
    # get_task = asyncio.create_task(manager.try_get_message_task(websocket))

    # await asyncio.gather(send_task, get_task)



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

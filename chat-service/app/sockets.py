from fastapi import APIRouter, WebSocket
import asyncio
import hashlib
from connection_manager import manager

socket_router = APIRouter()

# Функция для вычисления SHA-256 хеша файла
def calculate_file_hash(filename):
    sha256 = hashlib.sha256()
    with open(filename, "rb") as file:
        while chunk := file.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()



# @socket_router.websocket("/ws")
# async def send_message(websocket: WebSocket):
#     await manager.connect(websocket)
#     try:
#         while True:




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

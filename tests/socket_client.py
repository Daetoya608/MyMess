import asyncio
import websockets
import hashlib





async def download_file():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        await websocket.send("send_file large_file.txt")  # Запрос на файл

        expected_hash = None
        received_data = b""

        while True:
            chunk = await websocket.recv()
            if isinstance(chunk, str):  # Если пришел текст, проверяем его
                if chunk.startswith("hash:"):  # Это хеш-файл
                    expected_hash = chunk.split(":", 1)[1]
                    print(f"Получен хеш файла: {expected_hash}")
                elif chunk == "done":
                    break
                elif chunk.startswith("error"):
                    print(chunk)
                    return
            else:  # Иначе это бинарные данные
                received_data += chunk

        # Записываем загруженные данные в файл
        with open("/home/daetoya/files/downloaded_file.txt", "wb") as file:
            file.write(received_data)

        # Проверяем целостность файла
        sha256 = hashlib.sha256()
        sha256.update(received_data)
        calculated_hash = sha256.hexdigest()

        print(f"Вычисленный хеш: {calculated_hash}")

        if expected_hash and expected_hash == calculated_hash:
            print("✅ Файл загружен без ошибок!")
        else:
            print("❌ Файл поврежден! Нужно повторить загрузку.")

asyncio.run(download_file())

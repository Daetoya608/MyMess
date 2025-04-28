import asyncio
import json


class Client:
    def __init__(self, gui_to_client_queue, client_to_gui_queue):
        self.gui_to_client_queue = gui_to_client_queue
        self.client_to_gui_queue = client_to_gui_queue
        self.running = True

        self.handlers = {
            "send_text": self.handle_send_text,
            "connect": self.handle_connect,
            "disconnect": self.handle_disconnect,
            # другие команды
        }

    async def start(self):
        # Параллельно запускаем получение данных из GUI
        asyncio.create_task(self.listen_to_gui())

        # Здесь запускается твоя основная логика клиента
        await self.main_loop()

    async def listen_to_gui(self):
        while self.running:
            try:
                if not self.gui_to_client_queue.empty():
                    raw_msg = self.gui_to_client_queue.get()

                    # Если нужно, парсим JSON
                    msg = json.loads(raw_msg) if isinstance(raw_msg, str) else raw_msg

                    await self.dispatch_gui_command(msg)
            except Exception as e:
                print(f"[Client] Ошибка получения команды от GUI: {e}")

            await asyncio.sleep(0.1)

    async def dispatch_gui_command(self, msg):
        cmd_type = msg.get("type")
        handler = self.handlers.get(cmd_type, self.handle_unknown_command)
        await handler(msg.get("data"))

    async def handle_send_text(self, data):
        # Отправляем текстовое сообщение на сервер
        text = data.get("text", "")
        print(f"[Client] Отправка текста на сервер: {text}")
        # Здесь логика отправки по WebSocket или TCP

    async def handle_connect(self, data):
        print("[Client] Подключение к серверу...")
        # Логика подключения

    async def handle_disconnect(self, data):
        print("[Client] Отключение от сервера...")
        # Логика отключения

    async def handle_unknown_command(self, data):
        print(f"[Client] Неизвестная команда: {data}")

    async def main_loop(self):
        while self.running:
            i = 1
            test_dict = {
                "type": "new_message",
                "data": {
                    "chat_id": 123,
                    "sender": "Alice",
                    "text": "Привет!"
                }
            }

            # Основная работа клиента: приём сообщений от сервера и т.д.
            self.client_to_gui_queue.put(json.dumps(test_dict))
            await asyncio.sleep(1)

    def stop(self):
        self.running = False

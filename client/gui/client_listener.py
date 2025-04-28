import json
from PyQt5.QtCore import QThread, pyqtSignal
import time


class ClientListener(QThread):
    message_received = pyqtSignal(dict)  # Передаём весь словарь, не просто текст

    def __init__(self, client_to_gui_queue):
        super().__init__()
        self.client_to_gui_queue = client_to_gui_queue
        self.running = True

    def run(self):
        while self.running:
            try:
                if not self.client_to_gui_queue.empty():
                    raw_msg = self.client_to_gui_queue.get()

                    # Преобразуем строку в словарь (если нужно)
                    msg = json.loads(raw_msg) if isinstance(raw_msg, str) else raw_msg

                    self.message_received.emit(msg)
            except Exception as e:
                print(f"[ClientListener] Ошибка: {e}")
            time.sleep(0.1)

from typing import Set
from chat_creating_default_interface import CreatingChatDialogDefault
from PyQt5 import QtWidgets
import sys
from multiprocessing import Queue
from defaul_send_data_types import create_chat_request
import json


class ChatDialogManager:
    def __init__(self, gui_to_client_queue: Queue, client_to_gui_queue: Queue):
        self.gui_to_client_queue: Queue = gui_to_client_queue
        self.client_to_gui_queue: Queue = client_to_gui_queue
        self.added_members: Set[str] = set()
        self.chat_name: str = ""

    def add_new_member(self, line: str):
        if len(line) == 0 or line in self.added_members:
            return None
        self.added_members.add(line)
        return line

    def set_chat_name(self, chat_name: str):
        self.chat_name = chat_name

    def check_vars(self) -> bool:
        if len(self.chat_name) > 0 and len(self.added_members) > 0:
            return True
        return False

    def _send_to_client(self, data_json):
        self.gui_to_client_queue.put(data_json)

    def send_with_check(self) -> dict or None:
        if not self.check_vars():
            return None
        data = create_chat_request(self.chat_name, list(self.added_members))
        self._send_to_client(json.dumps(data))
        return data


class CreatingChatDialog(QtWidgets.QDialog):
    def __init__(self, gui_to_client_queue, client_to_gui_queue, parent=None):
        super().__init__(parent)
        self.dialog_manager = ChatDialogManager(gui_to_client_queue, client_to_gui_queue)
        # Создаем экземпляр UI и настраиваем интерфейс
        self.ui = CreatingChatDialogDefault()
        self.ui.setupUi(self)

        self.ui.add_members_button.clicked.connect(self.add_member_button_func)

    def add_member_button_func(self):
        text_from_line = self.ui.members_line.text()
        res = self.dialog_manager.add_new_member(text_from_line)
        if res is None:
            return
        button = QtWidgets.QPushButton(res)
        button.setFixedSize(100, 30)
        self.ui.added_members_horizontal_layout.addWidget(button)

    def confirm_data_button_func(self):
        


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dial = CreatingChatDialog(1,1)
    dial.show()
    sys.exit(app.exec_())


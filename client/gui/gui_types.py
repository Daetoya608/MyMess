from typing import List, Dict
from PyQt5 import QtWidgets


class MemberButton(QtWidgets.QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ChatButton(QtWidgets.QPushButton):
    def __init__(self, chat_name, chat_id):
        super().__init__(chat_name)
        self.chat_id = chat_id


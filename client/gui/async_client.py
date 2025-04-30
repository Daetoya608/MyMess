from PyQt5.QtCore import QObject, pyqtSignal
from ..client import Client
from ..client_settings import ClientSettings
from ..scripts import load_settings, update_settings, create_messages
from .window_manager import WindowManager
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from .gui_types import ChatButton
from ..server_requests import register, login, get_user_by_username
import sys
import asyncio
import websockets
import threading
from typing import List, Dict
from ..client_database import create_tables
from ..config import chat_uri, load_url_info


settings_data = load_settings()
client_settings = ClientSettings()
client = Client(client_settings)


app = QtWidgets.QApplication(sys.argv)

container = QWidget()
layout = QVBoxLayout()
layout.setContentsMargins(0, 0, 0, 0)
layout.setSpacing(0)
container.setLayout(layout)

window_manager = WindowManager(container)
container.setFixedSize(window_manager._current_window.size())


class AutoSetterData(QObject):
    chats_data_ready = pyqtSignal()
    def __init__(self):
        super().__init__()

    async def auto_set_save_data(self):
        await client.chats.auto_set_chats_members()
        await client.chats.auto_set_chats_messages()
        await client.chats.auto_set_users()
        await client.chats.auto_set_chat_names(client.settings.id)

        self.chats_data_ready.emit()


def registration_next_button_func():
    if not window_manager.all_window["reg_window"].is_correct_input_data():
        return
    data = window_manager.all_window["reg_window"].get_input_data()
    response = register(**data)
    if not response["status"]:
        return
    update_settings(data)
    window_manager.switch_to(window_manager.all_window["auth_window"])

def authentication_next_button_func():
    global client
    if not window_manager.all_window["auth_window"].is_correct_input_data():
        return
    data = window_manager.all_window["auth_window"].get_input_data()
    response = login(**data)
    print(f"!!!??? {response}")
    if not response["status"]:
        return
    update_settings(response)
    user_settings = load_settings()
    user_settings["password"] = data["password"]
    user_settings["nickname"] = ""
    client.settings.set_up_by_dict(user_settings)
    print(f"\nuser_settings={user_settings}")
    window_manager.switch_to(window_manager.all_window["chat_window"])

def add_self_user_to_chat():
    name = client.settings.username
    user = get_user_by_username(name)
    print("\n\n00000\n\n")
    if not user["status"]:
        print(11111)
        window_manager.all_window["create_chat_dialog"].reject()
    if user["user_id"] in window_manager.all_window["create_chat_dialog"].members_set:
        print(22222)
        return
    print(33333)
    window_manager.all_window["create_chat_dialog"].members_set.add(user["user_id"])
    window_manager.all_window["create_chat_dialog"].add_member_button_by_username(name)

def new_chat_button_func():
    print(f"\n\n\nNEW_CHAT_BUTTON_FUNC\n\n\n")
    add_self_user_to_chat()
    window_manager.all_window["create_chat_dialog"].exec_()

def create_chat_button_func():
    global client
    if not window_manager.all_window["create_chat_dialog"].is_correct_input_data():
        return
    chat_name = window_manager.all_window["create_chat_dialog"].get_chat_name()
    members = list(window_manager.all_window["create_chat_dialog"].members_set)
    client.sync_server_request_create_chat(chat_name, members)
    window_manager.all_window["create_chat_dialog"].accept()
    window_manager.all_window["create_chat_dialog"].clear_window()
    print("done")


def messages_to_str_format(messages: List[Dict]):
    if len(messages) == 0: return None
    result = ""
    for message in messages:
        user = client.chats.users[message["sender_id"]]
        line = f"{user['username']}: {message['content_text']}\n"
        result += line
    return result


def change_chat_func(chat_id: int):
    if chat_id == client.chats.current_chat_id:
        return
    client.chats.select_chat(chat_id)
    window_manager.all_window["chat_window"].prepare_message_enter()
    all_chat_messages = client.chats.chats_messages._data.get(chat_id, [])
    # print(f"_data = {client.chats.chats_messages._data}")
    # print(f"all_chat_messages: {all_chat_messages}")
    messages_str = messages_to_str_format(all_chat_messages)
    # print(f"\n!!!message_str = {messages_str}\n")
    window_manager.all_window["chat_window"].set_chat_simple_text(messages_str)
    print(client.chats.current_chat_id)


def add_new_chat_to_display(chat_id: int):
    global window_manager
    # print(f"\nadd_new_chat_to_display --- chat_id: {chat_id}\n")
    chat_name = client.chats.chat_names[chat_id]
    chat_button = ChatButton(chat_name, chat_id)
    chat_button.setGeometry(20, 20, 100, 30)
    chat_button.setSizePolicy(
        QtWidgets.QSizePolicy.Expanding,  # Горизонтальная политика
        QtWidgets.QSizePolicy.Fixed  # Вертикальная политика
    )
    chat_button.clicked.connect(
        lambda: change_chat_func(chat_id)
    )
    window_manager.all_window["chat_window"].ui.chats_vertical_layout.addWidget(chat_button)


def auto_set_buttons():
    global client
    for chat_id in client.chats.chat_names.keys():
        add_new_chat_to_display(chat_id)


def add_new_message_to_display(chat_id: int, message: Dict):
    if chat_id != client.chats.current_chat_id:
        return
    # print(f"\nadd_new_message_to_display---:{chat_id}: {message}\n")
    # print(f"\n{client.chats.users}\n")
    user = client.chats.users[message["sender_id"]]
    message_str = f"{user['username']}: {message['content_text']}\n"
    window_manager.all_window["chat_window"].append_to_end(message_str)


def send_button_func():
    message_line = window_manager.all_window["chat_window"].get_message_text()
    if len(message_line) == 0: return
    chat_id = client.chats.current_chat_id
    message_request_data = create_messages(message_line, chat_id)
    client.sync_sending_messages_queue.put(message_request_data)


auto_settings_data = AutoSetterData()
auto_settings_data.chats_data_ready.connect(auto_set_buttons)
client.chats.chats_messages.item_added.connect(add_new_message_to_display)
client.chats.chats_members.item_added.connect(add_new_chat_to_display)

# client.get_new_chat_handler_func = add_new_chat_to_display

window_manager.all_window["reg_window"].ui.next_button.clicked.connect(registration_next_button_func)
window_manager.all_window["auth_window"].ui.next_button.clicked.connect(authentication_next_button_func)
window_manager.all_window["create_chat_dialog"].ui.confirm_button.clicked.connect(create_chat_button_func)
window_manager.all_window["chat_window"].ui.send_button.clicked.connect(send_button_func)
window_manager.all_window["chat_window"].ui.new_chat_button.clicked.connect(new_chat_button_func)

async def websocket_client():
    global client
    await create_tables()
    uri = f"{chat_uri}/ws"
    while client.settings.token is None:
        await asyncio.sleep(0.1)
    await auto_settings_data.auto_set_save_data()
    print(f"\n\n\n\n!@#!@#!#!@!$!#$sjfnsjkdnfkdsjnf")
    # input(f"DDAWEQ")
    async with websockets.connect(uri, additional_headers={"token": client.settings.token}) as websocket:
        task1 = asyncio.create_task(client.receiver_handler_task(websocket))
        task2 = asyncio.create_task(client.get_message_task(websocket))
        task3 = asyncio.create_task(client.send_message_task(websocket))
        task4 = asyncio.create_task(client.put_from_sync_set_to_queue_task())
        task5 = asyncio.create_task(client.execute_operation_task())
        task6 = asyncio.create_task(client.update_users_info_task())

        await task1
        await task2
        await task3
        await task4
        await task5
        await task6

def gui_start():
    global container
    global app
    container.show()
    sys.exit(app.exec_())

def async_start():
    asyncio.run(websocket_client())

def main():
    async_thread = threading.Thread(target=async_start, daemon=True)
    async_thread.start()

    # Запускаем GUI в главном потоке
    gui_start()


if __name__ == '__main__':
    main()



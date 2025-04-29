from typing import Dict, List
from .client_database import (get_users_by_chat_id, get_unique_chat_ids, add_chat, add_connect, get_messages_by_chat_id,
                              get_unique_user_ids, get_user_by_user_id, User, get_unique_chats)
from .scripts import create_chat
import asyncio
from PyQt5.QtCore import QObject, pyqtSignal
from collections import UserDict

from collections.abc import MutableMapping


class ObservableMembersDict(QObject):
    item_added = pyqtSignal(object)  # Сигнал при добавлении (key, value)

    def __init__(self):
        super().__init__()
        self._data = {}  # Внутренний словарь

    def __setitem__(self, key, value):
        self._data[key] = value
        self.item_added.emit(key)

    def __getitem__(self, key):
        return self._data[key]


class ObservableMessagesDictWithList(QObject):
    item_added = pyqtSignal(object, object)  # Сигнал при добавлении (key, value)

    def __init__(self):
        super().__init__()
        self._data: Dict[int, List[Dict]] = dict()  # Внутренний словарь

    def __setitem__(self, key, value):
        self._data[key] = value

    def __getitem__(self, key):
        return self._data[key]

    def set(self, data: Dict):
        self._data = data.copy()

    def append_with_signal(self, chat_id: int, message: Dict):
        if self._data.get(chat_id) is None:
            self._data[chat_id] = []
        self._data[chat_id].append(message)
        self.item_added.emit(chat_id, message)


class ClientChats:

    def __init__(self):
        # храним словарь (ключ - индекс чата, значение - список индексов участников)
        # self.chats_members: Dict[int, List[int]] = dict()
        self.chats_members = ObservableMembersDict()
        self.current_chat_id = None
        self.users: Dict[int, Dict] = dict()
        # self.chats_messages: Dict[int, List[Dict]] = dict()
        self.chats_messages = ObservableMessagesDictWithList()
        self.chat_names: Dict[int, str] = dict()


    async def load_chats(self) -> Dict[int, List[int]]:
        chats = dict()
        chat_ids: List[int] = await get_unique_chat_ids()
        for chat_id in chat_ids:
            users_ids = await get_users_by_chat_id(chat_id)
            chats[chat_id] = users_ids
        return chats


    async def auto_set_chats_members(self):
        self.chats_members._data = await self.load_chats()


    def add_chat(self, chat_id: int, members_list: List[int]):
        print(f"\nadd_chat: chat_id={chat_id}")
        self.chats_members[chat_id] = members_list


    async def load_messages(self):
        result = dict()
        chat_ids: List[int] = await get_unique_chat_ids()
        for chat_id in chat_ids:
            messages_list = await get_messages_by_chat_id(chat_id)
            result[chat_id] = messages_list
        return result


    async def auto_set_chats_messages(self):
        messages = await self.load_messages()
        self.chats_messages.set(messages)


    def add_chat_message(self, chat_id: int, message: Dict):
        self.chats_messages.append_with_signal(chat_id, message)


    async def load_users(self):
        result = dict()
        users_ids = await get_unique_user_ids()
        for user_id in users_ids:
            user = await get_user_by_user_id(user_id)
            result[user_id] = user.to_dict()
        return users_ids


    async def auto_set_users(self):
        self.users = await self.load_users()


    def add_to_users_dict(self, user_info: Dict):
        if user_info is None:
            return
        self.users[user_info["user_id"]] = user_info


    async def load_chats_info(self):
        result = dict()
        all_chats = await get_unique_chats()
        for chat in all_chats:
            result[chat.id] = chat.chat_name
        return result


    async def auto_set_chat_names(self):
        self.chat_names = await self.load_chats_info()


    async def get_from_users(self, user_id):
        while user_id not in self.users:
            await asyncio.sleep(0.1)
        return self.users[user_id]


    # async def load_users_info(self, ):


    async def create_new_chat(self, chat_name: str, members_id: List[int]):
        new_chat = await add_chat(chat_name)
        if new_chat is None:
            # print("create_new_chat - creating chat error")
            return None
        successful_create_members = []
        for member_id in members_id:
            new_connection = await add_connect(member_id, new_chat.id)
            if new_connection is None:
                continue
            successful_create_members.append(new_connection.user_id)

        self.chats_members[new_chat.id] = successful_create_members
        return new_chat


    def select_chat(self, chat_id: int):
        self.current_chat_id = chat_id


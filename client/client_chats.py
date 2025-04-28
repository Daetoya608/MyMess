from typing import Dict, List
from client_database import get_users_by_chat_id, get_unique_chat_ids, add_chat, add_connect
from scripts import create_chat
import asyncio

class ClientChats:

    def __init__(self):
        # храним словарь (ключ - индекс чата, значение - список индексов участников)
        self.chats_members: Dict[int, List[int]] = dict()
        self.current_chat_id = None
        self.users: Dict[int, Dict] = dict()


    async def load_chats(self) -> Dict[int, List[int]]:
        chats = dict()
        chat_ids: List[int] = await get_unique_chat_ids()
        for chat_id in chat_ids:
            users_ids = await get_users_by_chat_id(chat_id)
            chats[chat_id] = users_ids
        return chats


    def add_to_users_dict(self, user_info: Dict):
        if user_info is None:
            return
        self.users[user_info["user_id"]] = user_info


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


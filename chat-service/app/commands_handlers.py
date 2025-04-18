from typing import Dict, List
from models import add_connect, add_chat
from chat_redis import store_new_chat

async def command_new_chat(chat_name: str, members: List[int]):
    new_chat = await add_chat(chat_name)
    if new_chat is None:
        return {
            "status": False
        }
    added_members = []
    for member in members:
        new_connection = await add_connect(member, new_chat.id)
        if new_connection is None:
            print(f"member: {member}, new_chat: {new_chat}")
            continue
        added_members.append(member)
    if len(added_members) > 0:
        await store_new_chat(new_chat.id, added_members)

    return {
        "status": True,
        "chat_id": new_chat.id,
        "members": added_members.copy(),
    }


async def command_handler(command: Dict):
    """
    :param command: =
    {
        "command": str, = (create_chat, )
        "chat_name": str = None
        "members": list[int]
    }

    :return: {
        "status": bool,
        "members": list[int]
    }
    """
    try:
        command_type = command["command"]
        if command_type == "create_chat":
            data = await command_new_chat(command["chat_name"], command["members"])
            return data
    except Exception as e:
        print(f"command_handler - Exception: {e}")
    return {
        "status": False,
    }

from typing import List, Dict
from .client_database import add_chat, add_connect, add_user_by_obj


async def operation_new_chat(chat_name: str, chat_id: int, members_id: List[int]):
    new_chat = await add_chat(chat_name, chat_id)
    if new_chat is None:
        # print("create_new_chat - creating chat error")
        return None
    successful_create_members = []
    for member_id in members_id:
        new_connection = await add_connect(member_id, new_chat.chat_id)
        if new_connection is None:
            continue
        successful_create_members.append(new_connection.user_id)

    print(f"created new chat - {new_chat.chat_name}, id={new_chat.chat_id}")
    return new_chat


# async def operation_handler(operation: Dict):
#     """
#
#     :param operation: ={
#         "operation": str, =(new_chat, )
#         "chat_id": int,
#         "chat_name": str,
#         "members": list[int]
#     }
#     :return Chat or None:
#     """
#     try:
#         operation_type = operation["operation"]
#         if operation_type == "new_chat":
#             new_chat = await operation_new_chat(operation["chat_name"], operation["members"])
#             print(f"\nchat_name={operation['chat_name']}\nchat_id={operation['chat_id']}\n")
#             return new_chat
#     except Exception as e:
#         print(f"operation_handler - Exception: {e}")
#         return None


async def user_info_handler(user_info: Dict):
    new_user = await add_user_by_obj(user_info)
    if new_user is None:
        # print(f"\nuser_info_handler - error, user_info = {new_user}")
        return None
    return new_user

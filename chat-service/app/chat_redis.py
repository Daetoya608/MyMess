import redis.asyncio as aioredis
import json
from schemas import MessageBase
from models import Connect, get_chats_by_user_id, get_unique_user_ids, get_users_by_chat_id, get_unique_chat_ids
from typing import List, Dict

redis_client = aioredis.Redis(host='localhost', port=6379, db=0)


async def load_users_by_chat_from_db(chat_id: int):
    user_connects: List[Connect] = await get_users_by_chat_id(chat_id)
    user_ids = [user_con.user_id for user_con in user_connects]
    key = f"chat:{chat_id}"
    await redis_client.rpush(key, *user_ids)


async def load_all_user_ids_from_db():
    chat_ids = await get_unique_chat_ids()
    for chat_id in chat_ids:
        await load_users_by_chat_from_db(chat_id)


async def get_users_by_chat_redis(chat_id: int):
    key = f"chat:{chat_id}"
    user_ids = await redis_client.lrange(key, 0, -1)
    return [json.loads(user_id.decode()) for user_id in user_ids]


async def store_message(chat_id: int, message_json: str):
    user_ids: List[int] = await get_users_by_chat_redis(chat_id)
    for user_id in user_ids:
        key = f"user:{user_id}"
        await redis_client.rpush(key, message_json)


async def get_all_user_messages(user_id):
    """Получает и удаляет все новые сообщения чата из Redis."""
    key = f"user:{user_id}"
    messages = await redis_client.lrange(key, 0, -1)  # Получаем все сообщения
    # redis_client.delete(key)  # Удаляем список после получения
    return [json.loads(msg.decode()) for msg in messages]  # Декодируем JSON


async def delete_all_user_messages(user_id):
    key = f"user:{user_id}"
    await redis_client.delete(key)


async def get_and_delete_all_user_messages(user_id):
    messages = await get_all_user_messages(user_id)
    size = len(messages)
    key = f"user:{user_id}"
    await redis_client.ltrim(key, size, -1)
    return messages


async def get_part_user_messages(user_id: int, limit: int = 20):
    key = f"user:{user_id}"
    messages = await redis_client.lrange(key, 0, limit - 1)
    return {i: json.loads(msg.decode()) for i, msg in enumerate(messages)}


async def delete_part_user_messages(user_id: int, limit: int = 20):
    key = f"chat:{user_id}"
    await redis_client.ltrim(key, limit, -1)


async def save_user_chats(user_id: int, chat_ids: List[int]):
    key = f"user:{user_id}"
    await redis_client.rpush(key, *chat_ids)


async def load_all_user_chats():
    user_ids: List[int] = await get_unique_user_ids()
    for user_id in user_ids:
        chat_ids = await get_chats_by_user_id(user_id)
        await save_user_chats(user_id, chat_ids)


async def get_chat_ids_by_user_id(user_id: int):
    key = f"user:{user_id}"
    chats = await redis_client.lrange(key, 0, -1)
    return [json.loads(chat.decode()) for chat in chats]


# # изменить
# async def get_all_messages_for_user_id(user_id: int) -> List[Dict]:
#     print("get_all_messages_for_user_id - {begins}")
#     chat_ids = await get_chat_ids_by_user_id(user_id)
#     result = []
#     for chat_id in chat_ids:
#         messages = await get_and_delete_all_chat_messages(chat_id)
#         # print(f"messages: {messages}")
#         result.extend(messages)
#     return result

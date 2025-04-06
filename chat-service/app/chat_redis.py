import redis.asyncio as aioredis
import json
from schemas import MessageBase
from models import get_chats_by_user_id, get_unique_user_ids
from typing import List, Dict

redis_client = aioredis.Redis(host='localhost', port=6379, db=0)


async def store_message(chat_id: int, message_json: str):
    """Сохраняет сообщение для чата в Redis."""
    key = f"chat:{chat_id}"
    await redis_client.rpush(key, message_json)  # Сохраняем как JSON-строку


async def get_all_chat_messages(chat_id):
    """Получает и удаляет все новые сообщения чата из Redis."""
    key = f"chat:{chat_id}"
    messages = await redis_client.lrange(key, 0, -1)  # Получаем все сообщения
    # redis_client.delete(key)  # Удаляем список после получения
    return [json.loads(msg.decode()) for msg in messages]  # Декодируем JSON


async def delete_all_chat_messages(chat_id):
    key = f"chat:{chat_id}"
    await redis_client.delete(key)


async def get_and_delete_all_chat_messages(chat_id):
    messages = await get_all_chat_messages(chat_id)
    size = len(messages)
    key = f"chat:{chat_id}"
    await redis_client.ltrim(key, size, -1)
    return messages


async def get_part_chat_messages(chat_id: int, limit: int = 20):
    key = f"chat:{chat_id}"
    messages = await redis_client.lrange(key, 0, limit - 1)
    return {i: json.loads(msg.decode()) for i, msg in enumerate(messages)}


async def delete_part_chat_messages(chat_id: int, limit: int = 20):
    key = f"chat:{chat_id}"
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


async def get_all_messages_for_user_id(user_id: int) -> List[Dict]:
    chat_ids = await get_chat_ids_by_user_id(user_id)
    result = []
    for chat_id in chat_ids:
        messages = await get_and_delete_all_chat_messages(chat_id)
        result.extend(messages)
    return result

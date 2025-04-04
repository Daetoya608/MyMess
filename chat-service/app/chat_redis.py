import redis.asyncio as aioredis
import json
from schemas import MessageBase

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


async def get_part_chat_messages(chat_id: int, limit: int = 20):
    key = f"chat:{chat_id}"
    messages = await redis_client.lrange(key, 0, limit - 1)
    return {i: json.loads(msg.decode()) for i, msg in enumerate(messages)}


async def delete_part_chat_messages(chat_id: int, limit: int = 20):
    key = f"chat:{chat_id}"
    await redis_client.ltrim(key, limit, -1)


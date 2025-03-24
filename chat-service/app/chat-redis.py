import redis.asyncio as aioredis
import json
from schemas import MessageBase

redis_client = aioredis.Redis(host='localhost', port=6379, db=0)


async def store_message(user_id: int, message: MessageBase):
    """Сохраняет сообщение для пользователя в Redis."""
    key = f"messages:{user_id}"
    await redis_client.rpush(key, message.model_dump_json())  # Сохраняем как JSON-строку


async def get_all_user_messages(user_id):
    """Получает и удаляет все новые сообщения пользователя из Redis."""
    key = f"messages:{user_id}"
    messages = await redis_client.lrange(key, 0, -1)  # Получаем все сообщения
    # redis_client.delete(key)  # Удаляем список после получения
    return [json.loads(msg.decode()) for msg in messages]  # Декодируем JSON


async def delete_all_user_messages(user_id):
    key = f"messages:{user_id}"
    await redis_client.delete(key)


async def get_part_user_messages(user_id: int, limit: int = 20):
    key = f"messages:{user_id}"
    messages = await redis_client.lrange(key, 0, limit - 1)
    return [json.loads(msg.decode()) for msg in messages]


async def delete_part_user_messages(user_id: int, limit: int = 20):
    key = f"messages:{user_id}"
    await redis_client.ltrim(key, limit, -1)



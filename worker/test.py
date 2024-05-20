import aioredis
import asyncio


async def send_to_redis(key, value):
    redis = aioredis.from_url("redis://redis")
    await redis.set(key, value)
    # Проверка, что значение установлено
    result = await redis.get(key)
    decoded_result = result.decode("utf-8") if result else None
    print(f"Значение для ключа '{key}' установлено: {decoded_result}")


# Запуск функции на верхнем уровне
asyncio.run(send_to_redis("test", "444"))

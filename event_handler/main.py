import asyncio

import aioredis
from pydantic import BaseModel


class EventInfo(BaseModel):
    camera_id: int
    class_name: str
    event_type: str


async def get_all_keys():
    redis = aioredis.from_url("redis://redis")
    keys = []
    cursor = "0"
    while cursor:
        cursor, result = await redis.scan(cursor)
        keys.extend(result)
    await redis.close()
    print(keys)
    return keys


async def get_all_keys_and_values():
    redis = aioredis.from_url("redis://redis")
    keys = []
    cursor = "0"
    while cursor:
        cursor, result = await redis.scan(cursor)
        keys.extend(result)

    values = await redis.mget(*keys)  # получаем значения по всем ключам сразу
    await redis.close()

    # соединяем ключи и значения в словарь
    keys_and_values = dict(zip(keys, values))
    print(keys_and_values)
    return keys_and_values


async def main():
    await get_all_keys_and_values()


if __name__ == "__main__":
    asyncio.run(main())

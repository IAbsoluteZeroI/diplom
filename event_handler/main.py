import asyncio
import aioredis
from pydantic import BaseModel


class EventInfo(BaseModel):
    camera_id: int
    class_name: str
    event_type: str


class Handler:
    def __init__(self):
        self.redis = aioredis.from_url("redis://redis")

    async def get_all_keys(self):
        keys = []
        cursor = b"0"
        while cursor:
            cursor, result = await self.redis.scan(cursor)
            keys.extend(result)
        return keys

    async def get_all_keys_and_values(self, keys, model: BaseModel):
        instances = []
        for key in keys:
            json_data = await self.redis.get(key)
            if json_data:
                instance = model.parse_raw(json_data)
                instances.append(instance)
                # await self.redis.delete(key)
        return instances

    async def close(self):
        await self.redis.close()


async def main():
    handler = Handler()
    try:
        while True:
            keys = await handler.get_all_keys()
            if keys:
                instances = await handler.get_all_keys_and_values(keys, EventInfo)
                print(instances)
            await asyncio.sleep(10)  # Ждем 10 секунд перед следующим циклом
    finally:
        await handler.close()


if __name__ == "__main__":
    asyncio.run(main())

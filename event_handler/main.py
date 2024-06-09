import asyncio
import aioredis
from pydantic import BaseModel


class EventInfo(BaseModel):
    camera_id: int
    class_name: str
    event_type: str
    frame_num: int


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
        events = []
        for key in keys:
            json_data = await self.redis.get(key)
            if json_data:
                instance = model.model_validate_json(json_data)
                events.append(instance)
                # await self.redis.delete(key)
                
        return events

    async def close(self):
        await self.redis.close()


async def main():
    handler = Handler()
    
    try:
        while True:
            print()
            keys = await handler.get_all_keys()
            
            if keys:
                
                events = await handler.get_all_keys_and_values(keys, EventInfo)
                
                for event in events:
                    print(event)
                    
                    
            await asyncio.sleep(10)  # Ждем 10 секунд перед следующим циклом
    finally:
        await handler.close()


if __name__ == "__main__":
    asyncio.run(main())

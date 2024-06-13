import asyncio

import aioredis
import requests
from pydantic import BaseModel


class EventInfo(BaseModel):
    camera_id: int
    class_name: str
    event_type: str
    frame_num: int
    line_id: int


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
                events.append((key, instance))

        return events

    async def delete_keys(self, keys):
        if keys:
            await self.redis.delete(*keys)

    async def close(self):
        await self.redis.close()


def get_related_camera_id(camera_id):
    response = requests.get(f"http://web:8000/cameras/{camera_id}/")
    if response.status_code == 200:
        data = response.json()
        return data.get("camera_id")
    return None


async def process_events():
    handler = Handler()
    urlPOST = "http://web:8000/add_event"

    try:
        while True:
            # Получить все ключи из Redis
            keys = await handler.get_all_keys()

            if keys:
                # Получить все события из Redis
                key_event_pairs = await handler.get_all_keys_and_values(keys, EventInfo)
                in_events = {}
                out_events = {}

                for key, event in key_event_pairs:
                    if event.event_type == "IN":
                        in_events[key] = event
                    elif event.event_type == "OUT":
                        out_events[key] = event

                matched_keys = set()
                while in_events and out_events:
                    in_key, in_event = min(
                        in_events.items(), key=lambda x: x[1].frame_num
                    )
                    related_camera_id = get_related_camera_id(in_event.camera_id)

                    if related_camera_id:
                        # Найти соответствующее событие OUT
                        out_event_pair = min(
                            (
                                (key, event)
                                for key, event in out_events.items()
                                if event.camera_id == related_camera_id
                            ),
                            key=lambda x: x[1].frame_num,
                            default=None,
                        )

                        if out_event_pair:
                            out_key, out_event = out_event_pair

                            # Формируем данные для отправки
                            data = {
                                "frame": in_event.frame_num,
                                "object": in_event.class_name,
                                "from_place": out_event.camera_id,
                                "to_place": in_event.camera_id,
                            }
                            requests.post(urlPOST, data=data)

                            # Удаляем соответствующие события из словарей и добавляем ключи в список для удаления из Redis
                            matched_keys.update([in_key, out_key])
                            del in_events[in_key]
                            del out_events[out_key]
                        else:
                            break
                    else:
                        break

                # Удаляем сматченные события из Redis
                if matched_keys:
                    await handler.delete_keys(list(matched_keys))

            await asyncio.sleep(10)
    finally:
        await handler.close()


if __name__ == "__main__":
    asyncio.run(process_events())

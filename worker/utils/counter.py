import asyncio
from typing import Dict, List

import aioredis
import numpy as np
from pydantic import BaseModel
from supervision.geometry.dataclasses import Point, Vector
from supervision.tools.detections import Detections


class EventInfo(BaseModel):
    camera_id: int
    class_name: str
    event_type: str


class CustomLineCounter:
    def __init__(
        self,
        start: Point,
        end: Point,
        classes: List,
        camera_id: int,
        class_name_dict: dict,
    ):
        self.vector = Vector(start=start, end=end)
        self.tracker_state: Dict[str, bool] = {}
        self.start = start
        self.end = end
        self.camera_id = camera_id
        self.class_name_dict = class_name_dict
        self.redis = aioredis.from_url("redis://redis")
        self.result_dict = {
            int(class_id): {"in": [], "out": []} for class_id in classes
        }

    async def send_to_redis(self, key, value):
        # Ensure key and value are of the correct type
        key = str(key)
        value = str(value)
        await self.redis.set(key, value)
        result = await self.redis.get(key)
        decoded_result = result.decode("utf-8") if result else None
        print(f"Значение для ключа '{key}' установлено: {decoded_result}")

    async def update(self, detections: Detections):
        tasks = []
        for id in detections.class_id:
            mask = np.array(
                [class_id in [int(id)] for class_id in detections.class_id], dtype=bool
            )
            filtereddet = detections.filter(mask=mask, inplace=False)

            for xyxy, confidence, class_id, tracker_id in filtereddet:
                # handle detections with no tracker_id
                if tracker_id is None:
                    continue

                # we check if all four anchors of bbox are on the same side of vector
                x1, y1, x2, y2 = xyxy
                anchors = [
                    Point(x=x1, y=y1),
                    Point(x=x1, y=y2),
                    Point(x=x2, y=y1),
                    Point(x=x2, y=y2),
                ]
                triggers = [self.vector.is_in(point=anchor) for anchor in anchors]

                # detection is partially in and partially out
                if len(set(triggers)) == 2:
                    continue

                tracker_state = triggers[0]
                # handle new detection
                if tracker_id not in self.tracker_state:
                    self.tracker_state[tracker_id] = tracker_state
                    continue

                # handle detection on the same side of the line
                if self.tracker_state.get(tracker_id) == tracker_state:
                    continue

                self.tracker_state[tracker_id] = tracker_state
                if tracker_state:
                    print(f"{self.camera_id} IN :: {self.class_name_dict[class_id]}")
                    tasks.append(
                        self.send_to_redis(
                            tracker_id,
                            EventInfo(
                                camera_id=self.camera_id,
                                class_name=self.class_name_dict[class_id],
                                event_type="IN",
                            ).json(),
                        )
                    )
                    # tasks.append(self.send_to_redis(tracker_id, "in"))
                else:
                    print(f"{self.camera_id} OUT :: {self.class_name_dict[class_id]}")
                    tasks.append(
                        self.send_to_redis(
                            tracker_id,
                            EventInfo(
                                camera_id=self.camera_id,
                                class_name=self.class_name_dict[class_id],
                                event_type="OUT",
                            ).json(),
                        )
                    )
                    # tasks.append(self.send_to_redis(tracker_id, "out"))

        if tasks:
            await asyncio.gather(*tasks)

from typing import List, Dict
import json
from ...base.models_interfaces import *
from .custom_json_encoder import serialize, deserialize
from ..models import Camera, CustomLineCounter, Place, ObjectsInPlace


class JSONDBManager:
    def __init__(self):
        self.filename = "app/model/data/data.json"

    def read_data(self) -> Dict[str, List[dict]]:
        with open(self.filename, "r") as file:
            data = json.load(file)
        return data

    def write_data(self, data: Dict[str, List[dict]]):
        print(f"writing {self.filename}")
        with open(self.filename, "w") as file:
            json.dump(data, file, indent=4)

    def get_objects_in_place(self) -> List[IObjectsInPlace]:
        data = self.read_data().get("objects_in_place", [])
        return [IObjectsInPlace(**item) for item in data]

    def add_object_in_place(self, obj: IObjectsInPlace):
        data = self.read_data()
        data["objects_in_place"].append(vars(obj))
        self.write_data(data)

    def get_places(self) -> List[IPlace]:
        data = self.read_data().get("places", [])
        return [IPlace(**item) for item in data]

    def add_place(self, place: IPlace):
        data = self.read_data()
        data["places"].append(vars(place))
        self.write_data(data)

    def get_custom_line_counters(self) -> List[ICustomLineCounter]:
        data = self.read_data().get("custom_line_counters", [])
        return [ICustomLineCounter(**item) for item in data]

    def add_custom_line_counter(self, line_counter: ICustomLineCounter):
        data = self.read_data()
        data["custom_line_counters"].append(vars(line_counter))
        self.write_data(data)

    def get_event_histories(self) -> List[IEventHistory]:
        data = self.read_data().get("event_histories", [])
        return [IEventHistory(**item) for item in data]

    def add_event_history(self, event_history: IEventHistory):
        data = self.read_data()
        data["event_histories"].append(vars(event_history))
        self.write_data(data)

    def get_cameras(self) -> List[ICamera]:
        data = self.read_data().get("cameras", [])
        cameras = []
        for camera in data:
            camera_data = deserialize(camera)
            cameras.append(
                Camera(
                    id=camera_data["id"],
                    line_counter=CustomLineCounter(
                        id=camera_data["line_counters"][0]["id"],
                        coord_left=Point(
                            x=camera_data["line_counters"][0]["coord_left"][0],
                            y=camera_data["line_counters"][0]["coord_left"][1],
                        ),
                        coord_right=Point(
                            x=camera_data["line_counters"][0]["coord_right"][0],
                            y=camera_data["line_counters"][0]["coord_right"][1],
                        ),
                    ),
                    video_path=camera_data["video_path"],
                    place=Place(
                        objects=(
                            ObjectsInPlace(
                                chair=camera_data["place"]["objects_in_place"]["chair"],
                                person=camera_data["place"]["objects_in_place"][
                                    "person"
                                ],
                                interactive_whiteboard=camera_data["place"][
                                    "objects_in_place"
                                ]["interactive_whiteboard"],
                                keyboard=camera_data["place"]["objects_in_place"][
                                    "keyboard"
                                ],
                                monitor=camera_data["place"]["objects_in_place"][
                                    "monitor"
                                ],
                                pc=camera_data["place"]["objects_in_place"]["pc"],
                                table=camera_data["place"]["objects_in_place"]["table"],
                                id=camera_data["place"]["objects_in_place"]["id"],
                            )
                            if camera_data["place"]["objects_in_place"] is not None
                            else None
                        )
                    ),
                )
            )

        return cameras

    def add_camera(self, camera: ICamera):
        data = self.read_data()
        camera_data = serialize(camera)
        print(camera_data)
        data["cameras"].append(camera_data)
        self.write_data(data)

    def get_objs(self) -> List[IObj]:
        data = self.read_data().get("objs", [])
        return [IObj(**item) for item in data]

    def add_obj(self, obj: IObj):
        data = self.read_data()
        data["objs"].append(vars(obj))
        self.write_data(data)


json_db_manager = JSONDBManager()

from ...base.models_interfaces import *
import json


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, IPlace):
            return {
                "id": obj.id,
                "objects": obj.objects.__dict__,
                "cameras": [camera.id for camera in obj.cameras],
            }
        elif isinstance(obj, ICustomLineCounter):
            return {
                "id": obj.id,
                "coord_left": obj.coord_left,
                "coord_right": obj.coord_right,
                "events": [event.id for event in obj.events],
            }
        elif isinstance(obj, IEventHistory):
            return {
                "id": obj.id,
                "line_counter": obj.line_counter.id,
                "obj": obj.obj.__dict__,
                "date": obj.date,
                "type": obj.type.value,
            }
        elif isinstance(obj, ICamera):
            formatted_line_counters = []
            for line_counter in obj.line_counters:
                events_data = []
                for event in line_counter.events:
                    event_data = {
                        "id": event.id,
                        "obj": {"id": event.obj.id, "name": event.obj.name},
                        "date": event.date.strftime("%Y-%m-%d %H:%M:%S"),
                        "type": event.type.name,
                    }
                    events_data.append(event_data)

                formatted_line_counter = {
                    "id": line_counter.id,
                    "coord_left": line_counter.coord_left.as_xy_int_tuple(),
                    "coord_right": line_counter.coord_right.as_xy_int_tuple(),
                    "events": events_data,
                }
                formatted_line_counters.append(formatted_line_counter)

            return {
                "id": obj.id,
                "line_counters": formatted_line_counters,
                "place": {
                    "id": obj.place.id,
                    "objects_in_place": (
                        obj.place.objects.__dict__
                        if obj.place.objects is not None
                        else None
                    ),
                },
                "video_path": obj.video_path,
            }
        elif isinstance(obj, IObj):
            return {
                "id": obj.id,
                "name": obj.name,
                "events": [event.id for event in obj.events],
            }
        return super().default(obj)


def serialize(obj):
    return json.dumps(obj, cls=CustomJSONEncoder)


def deserialize(json_str):
    def as_enum(d):
        if "type" in d:
            return EventType(d["type"])
        return d

    return json.loads(json_str, object_hook=as_enum)

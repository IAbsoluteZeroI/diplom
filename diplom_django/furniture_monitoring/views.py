import re
import math
import docker
import threading
from django.db.models import Q
from rest_framework import status
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import EventHistorySerializer
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect, render, reverse
from .models import Camera, EventHistory, LineCounter, Object, Place, ObjectsInPlace

object_names ={
    'person': 'Человек',
    'chair': 'Стул',
    'interactive whiteboard': 'Интерактивная доска',
    'keyboard': 'Клавиатура',
    'laptop': 'Ноутбук',
    'monitor': 'Монитор',
    'pc': 'Системный блок',
    'table': 'Стол',
}

client = docker.from_env()

class CameraGraphView(APIView):
    def get(self, request, cam_id):
        camera_id = LineCounter.objects.filter(
            id__in=LineCounter.objects.filter(camera=cam_id).values_list(
                "line_id", flat=True
            )
        ).values_list("camera", flat=True)
        data = {"camera_id": camera_id.first()}

        return Response(data, status=status.HTTP_200_OK)


class CreateEvent(APIView):
    def post(self, request):
        serializer = EventHistorySerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            print(data)
            update_object_quantity(data)
            if Object.objects.filter(name=data["object"]):
                event = EventHistory(
                    frame=data["frame"],
                    object=data["object"],
                    from_place=data["from_place"],
                    to_place=data["to_place"],
                )
                event.save()
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def update_object_quantity(data):
    
    object_instance = (
        Object.objects.get(name=data['object'])
        )
    from_place_instance = (
        Place.objects.get( id=CameraIdToPlaceID(data['from_place']))
        )
    to_place_instance = (
        Place.objects.get(id=CameraIdToPlaceID(data['to_place']))
        )

    objects_in_from_place = ObjectsInPlace.objects.get(
        object=object_instance.id,
        place=from_place_instance.id)
    print(objects_in_from_place)
    objects_in_from_place.quantity -= 1
    objects_in_from_place.save()
    
    objects_in_to_place = ObjectsInPlace.objects.get(
        object=object_instance.id,
        place=to_place_instance.id)
    print(objects_in_to_place)
    objects_in_to_place.quantity += 1
    objects_in_to_place.save()

def collect_floors():
    cameras = Camera.objects.all()
    unique_floors = set()
    for camera in cameras:
        floors = re.split(r"[-,\s]", camera.floor)
        for floor in floors:
            if floor != "5":
                unique_floors.add(floor.strip())
    return unique_floors

def CameraIdToPlaceID(id):
    place_id=Camera.objects.filter(id=id).values_list("place_id", flat=True).first()
    return place_id

def CameraIdToPlaceName(id):
    place_name = Place.objects.filter(
        id=Camera.objects.filter(id=id).values_list("place_id", flat=True).first()
        ).values_list("name", flat=True ).first()
    return place_name

def GetPlaceName(id):
    place_name = Place.objects.filter(id=id).values_list("name", flat=True ).first()
    return place_name

@csrf_protect
def floor_detail(request, floor):
    
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        place_id = request.POST.get("place_id")
        if place_id:
            
            context = {'place_id': GetPlaceName(place_id)}
            
            camera_ids = list(map(str, Camera.objects.filter(place_id=place_id).values_list("id", flat=True)))
            events = EventHistory.objects.filter(
                Q(from_place__in=camera_ids) | Q(to_place__in=camera_ids)
            ).order_by("id")
            event_data = []
            for event in events:
                event_data.append({
                    'object': object_names[event.object],
                    'from_place': CameraIdToPlaceName(event.from_place),
                    'to_place': CameraIdToPlaceName(event.to_place),
                    'frame': f"{math.ceil(event.frame/30)} секунда"
                })

            items = ObjectsInPlace.objects.filter(place_id=place_id).order_by("id")
            
            item_data = []
            for item in items:
                item_data.append({
                    'object': object_names[item.object.name],
                    'count': item.quantity,
                })

            context["events"] = 0 if len(event_data) == 0 else event_data
            context["items"] = 0 if len(item_data) == 0 else item_data

            return JsonResponse(context)

    cameras_on_floor = Camera.objects.filter(
        floor__iregex=rf"(^|[-,\s]){floor}([-,\s]|$)"
    )
    places_on_floor = Place.objects.filter(cameras__in=cameras_on_floor).distinct()
    
    places_and_cameras = {
        place: place.cameras.filter(floor__iregex=rf"(^|[-,\s]){floor}([-,\s]|$)")
        for place in places_on_floor
    }

    context = {
        "floor": floor,
        "places_and_cameras": places_and_cameras,
        "floors": sorted(collect_floors()),
        "events": 0,
        "items": 0
    }

    return render(request, "furniture_monitoring/floor_detail.html", context)


def start_worker(filepath, cam_id, x1, y1, x2, y2, line_id):
    client.containers.run(
        "diplom-worker",
        [
            "python3",
            "main.py",
            "--file-path",
            filepath,
            "--camera-id",
            str(cam_id),
            "--start-xy",
            str(x1),
            str(y1),
            "--end-xy",
            str(x2),
            str(y2),
            "--line-id",
            str(line_id),
        ],
        remove=True,
        name=f"worker_{cam_id}",
        network="diplom_default",
        device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])],
        volumes={"diplom_media": {"bind": "/app/media", "mode": "rw"}},
    )


def stop_worker(worker_name):
    try:
        container = client.containers.get(worker_name)
        container.stop()
        container.remove()
    except docker.errors.NotFound:
        print(f"Container {worker_name} not found.")


def get_worker_container_numbers():
    containers = client.containers.list()

    pattern = re.compile(r"worker_(\d+)")

    worker_numbers = []
    for container in containers:
        match = pattern.search(container.name)
        if match:
            worker_numbers.append(int(match.group(1)))

    worker_numbers.sort()
    return worker_numbers


@csrf_protect
def index(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "start_tracking":
            selected_counters = request.POST.getlist("selected_counters[]")
            selected_line_counters = LineCounter.objects.filter(
                id__in=selected_counters
            )

            threads = []
            for line_counter in selected_line_counters:
                line_counter: LineCounter
                camera: Camera = line_counter.camera
                thread = threading.Thread(
                    target=start_worker,
                    args=(
                        camera.video_path,
                        camera.id,
                        int(line_counter.start_x),
                        int(line_counter.start_y),
                        int(line_counter.end_x),
                        int(line_counter.end_y),
                        int(line_counter.line_id),
                    ),
                )
                thread.start()
                threads.append(thread)

            return redirect(reverse("index"))

        elif action == "stop_tracking":
            selected_counters = request.POST.getlist("selected_counters[]")
            selected_line_counters = LineCounter.objects.filter(
                id__in=selected_counters
            )
            for line_counter in selected_line_counters:
                camera: Camera = line_counter.camera
                stop_worker(f"worker_{camera.id}")

            return redirect(reverse("index"))
        else:
            pass
    else:
        context = {
            "floors": sorted(collect_floors()),
        }
        context["line_counters"] = LineCounter.objects.all().order_by("id")
        context["worker_numbers"] = get_worker_container_numbers()

        return render(request, "furniture_monitoring/index.html", context)

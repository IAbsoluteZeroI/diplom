import threading
import re
import docker
from django.db import connection
from django.shortcuts import redirect, render, reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from .models import Camera, LineCounter, Place

client = docker.from_env()

def collect_floors():
    cameras = Camera.objects.all()
    unique_floors = set()
    for camera in cameras:
        floors = re.split(r'[-,\s]', camera.floor)
        for floor in floors:
            if floor != '5':
                unique_floors.add(floor.strip())
    return unique_floors

def index(request):
    context = {
        'floors': sorted(collect_floors()),
    }
    return render(request, "furniture_monitoring/index.html", context)

def floor_detail(request, floor):
    cameras_on_floor = Camera.objects.filter(
        floor__iregex=rf'(^|[-,\s]){floor}([-,\s]|$)'
    )
    
    places_on_floor = Place.objects.filter(cameras__in=cameras_on_floor).distinct()
    
    places_and_cameras = {
        place: place.cameras.filter(floor__iregex=rf'(^|[-,\s]){floor}([-,\s]|$)') for place in places_on_floor
    }

    context = {
        'floor': floor,
        'places_and_cameras': places_and_cameras,
        'floors': sorted(collect_floors()),
    }
    return render(request, 'furniture_monitoring/floor_detail.html', context)


def start_worker(filepath, cam_id, x1, y1, x2, y2):
    client = docker.from_env()
    
    volumes = {
        'diplom_media': {
            'bind': '/app/media',
            'mode': 'rw'
        }
    }

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
        ],
        remove=True,
        name=f"worker_{cam_id}",
        network="diplom_default",
        device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])],
        volumes=volumes
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
def track_cameras_view(request):
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
                    ),
                )
                thread.start()
                threads.append(thread)

            return redirect(reverse("track_cameras"))

        elif action == "stop_tracking":
            selected_counters = request.POST.getlist("selected_counters[]")
            selected_line_counters = LineCounter.objects.filter(
                id__in=selected_counters
            )
            for line_counter in selected_line_counters:
                camera: Camera = line_counter.camera
                stop_worker(f"worker_{camera.id}")

            return redirect(reverse("track_cameras"))
        else:
            pass
    else:
        context = {
            'floors': sorted(collect_floors()),
        }
        context["line_counters"] = LineCounter.objects.all().order_by("id")
        context["worker_numbers"] = get_worker_container_numbers()

        return render(request, "furniture_monitoring/track_cameras.html", context)

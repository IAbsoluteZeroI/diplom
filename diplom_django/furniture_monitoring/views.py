import threading
import re
import docker
from django.db import connection
from django.shortcuts import redirect, render, reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from .models import Camera, LineCounter

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
    # Получение всех уникальных значений этажей из базы данных
    context = {
        'floors': sorted(collect_floors()),
    }
    return render(request, "furniture_monitoring/index.html", context)

def floor_detail(request, floor):
    # Получение камер для выбранного этажа, включая многоуровневые этажи
    cameras_on_floor = Camera.objects.filter(
        floor__iregex=rf'(^|[-,\s]){floor}([-,\s]|$)'
    )
    
    context = {
        'floor': floor,
        'cameras_on_floor': cameras_on_floor,
        'floors': sorted(collect_floors()),
    }
    return render(request, 'furniture_monitoring/floor_detail.html', context)


def start_worker(filepath, cam_id, x1, y1, x2, y2):
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
        # name=get_next_worker_name(),
        name=f"worker_{cam_id}",
        network="diplom_default",
        device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])],
    )


def stop_worker(worker_name):
    try:
        container = client.containers.get(worker_name)
        container.stop()
        container.remove()
    except docker.errors.NotFound:
        print(f"Container {worker_name} not found.")


def db_tables_view(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )
        table_names = [row[0] for row in cursor.fetchall()]
    
    context = {
        "table_names": table_names,
        'floors': sorted(collect_floors()),
    }
    
    return render(request, "furniture_monitoring/db_tables.html", context)


def table_view(request, table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

    context = {
        "table_name": table_name,
        "column_names": column_names,
        "rows": rows,
        'floors': sorted(collect_floors()),
    }
    return render(request, "furniture_monitoring/table.html", context)


def get_worker_container_numbers():
    # Получение всех контейнеров
    containers = client.containers.list()

    # Регулярное выражение для соответствия именам контейнеров worker_n
    pattern = re.compile(r"worker_(\d+)")

    # Извлечение номеров n из имен контейнеров
    worker_numbers = []
    for container in containers:
        match = pattern.search(container.name)
        if match:
            worker_numbers.append(int(match.group(1)))

    # Сортировка номеров для упорядоченного отображения
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

            # TODO: Сейчас страница обновляется через 5 секунды после запуска контейнеров,
            # а после завершения их работы нет. Желательно обновить страницу и через 5 сек,
            # и после завершения контейнеров. Надо как то обновить страницу, не потеряв
            # threads, или обработать завершение контейнеров по-другому.

            # Обновить страницу через 5 сек
            #time.sleep(5)
            return redirect(reverse("track_cameras"))
            # Дождаться выполнения всех контейнеров и обновить страницу
            # for thread in threads:
            #     tread.join()
            # return redirect(reverse("track_cameras"))

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

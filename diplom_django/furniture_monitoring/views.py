import subprocess

from django.db import connection
from django.http import HttpResponse
from django.shortcuts import redirect, render, reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

import docker
client = docker.from_env()

from .models import Camera, LineCounter

def get_next_worker_name():
    existing_containers = client.containers.list(all=True)
    existing_names = [container.name for container in existing_containers]

    # Начинаем счет с worker_1
    i = 1
    while True:
        candidate_name = f"worker_{i}"
        if candidate_name not in existing_names:
            return candidate_name
        i += 1


# Create your views here.
def index(request):
    context = {}
    return render(request, "furniture_monitoring/index.html", context)


def db_tables_view(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )
        table_names = [row[0] for row in cursor.fetchall()]

    return render(
        request, "furniture_monitoring/db_tables.html", {"table_names": table_names}
    )


def table_view(request, table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

    context = {
        "table_name": table_name,
        "column_names": column_names,
        "rows": rows,
    }
    return render(request, "furniture_monitoring/table.html", context)


@csrf_protect
def track_cameras_view(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "start_tracking":
            # Get the selected line counters
            selected_counters = request.POST.getlist("selected_counters[]")
            selected_line_counters = LineCounter.objects.filter(
                id__in=selected_counters
            )
            print(selected_line_counters)
            # Call your function to start tracking with the selected line counters
            container = client.containers.run("diplom-worker",
                                              ["python3", "main.py", "--file-path", "kab24.avi", "--camera-id", "1", "--start-xy", "1200", "750", "--end-xy", "1100", "230"],
                                              remove=True,
                                              name = get_next_worker_name(),
                                              network="diplom_default",
                                              device_requests=[
                                                  docker.types.DeviceRequest(
                                                      count=-1,
                                                      capabilities=[['gpu']
                                                                    ])])

            print(container.logs().decode('utf-8'))
            # redirect to the same page after processing
            return redirect(reverse("track_cameras"))
        elif action == "stop_tracking":
            selected_counters = request.POST.getlist("selected_counters[]")
            selected_line_counters = LineCounter.objects.filter(
                id__in=selected_counters
            )
            # Call your function to stop tracking here
            # redirect to the same page after processing
            return redirect(reverse("track_cameras"))
        else:
            # Handle invalid action if needed
            pass
    else:
        context = {}
        context["line_counters"] = LineCounter.objects.all().order_by("id")[:2]
        return render(request, "furniture_monitoring/track_cameras.html", context)

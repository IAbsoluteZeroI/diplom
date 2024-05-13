import subprocess

from django.db import connection
from django.http import HttpResponse
from django.shortcuts import redirect, render


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

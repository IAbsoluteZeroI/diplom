from django.shortcuts import render
from django.http import HttpResponse
import subprocess
from django.shortcuts import render, redirect
# Create your views here.
def index(request):
    context = {}
    return render(request, "furniture_monitoring/index.html", context)


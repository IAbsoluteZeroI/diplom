from django.shortcuts import render
from django.http import HttpResponse
import subprocess

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the index.")


from django.contrib import admin
from .models import Place, Camera, LineCounter, ObjectsInPlace, EventHistory, Object

# Register your models here.

admin.site.register(Place)
admin.site.register(Camera)
admin.site.register(LineCounter)
admin.site.register(ObjectsInPlace)
admin.site.register(EventHistory)
admin.site.register(Object)

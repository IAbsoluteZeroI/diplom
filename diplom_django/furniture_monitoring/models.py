from django.contrib.postgres.fields import ArrayField
from django.db import models


class Object(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class LineCounter(models.Model):
    id = models.AutoField(primary_key=True)
    camera = models.ForeignKey(
        "Camera", on_delete=models.CASCADE, related_name="line_counters"
    )
    start_x = models.FloatField(default=0)
    start_y = models.FloatField(default=0)
    end_x = models.FloatField(default=0)
    end_y = models.FloatField(default=0)

    def __str__(self):
        return f"LineCounter {self.id} for Camera {self.camera.place.name}"


class Camera(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    place = models.ForeignKey("Place", on_delete=models.CASCADE, related_name="cameras", blank=True, null=True, default="")
    floor = models.CharField(max_length=5)
    wing = models.CharField(max_length=6)
    video_path = models.CharField(max_length=255, blank=True, null=True, default="")

    def __str__(self):
        return f"{self.name}"


class Place(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True, null=True, default="")
    
    def __str__(self):
        return self.name


class ObjectsInPlace(models.Model):
    id = models.AutoField(primary_key=True)
    object = models.ForeignKey(
        "Object", on_delete=models.CASCADE, related_name="object"
    )
    place = models.ForeignKey(
        "Place", on_delete=models.CASCADE, related_name="place"
    )
    quantity = models.IntegerField(default=0)
    
    def __str__(self):
        return f"ObjectsInPlace {self.place.name}"


class EventHistory(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=3)
    frame = models.IntegerField(default=0)
    object = models.CharField(max_length=100)
    from_place = models.CharField(max_length=100)
    to_place = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Event {self.id} at {self.frame} frame"

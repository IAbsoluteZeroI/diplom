from django.contrib.postgres.fields import ArrayField
from django.db import models


class Object(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class LineCounter(models.Model):
    id = models.AutoField(primary_key=True)
    camera = models.ForeignKey(
        "Camera", on_delete=models.CASCADE, related_name="line_counters"
    )
    coord_left = ArrayField(models.FloatField(), size=2)
    coord_right = ArrayField(models.FloatField(), size=2)
    related_line_counter = models.ForeignKey(
        "LineCounter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_line_counters",
    )
    event_history = models.ForeignKey(
        "EventHistory", on_delete=models.CASCADE, related_name="event_histories"
    )

    def __str__(self):
        return f"LineCounter {self.id} for Camera {self.camera.id}"


class Camera(models.Model):
    id = models.AutoField(primary_key=True)
    place = models.ForeignKey("Place", on_delete=models.CASCADE, related_name="cameras")

    def __str__(self):
        return f"Camera {self.id} in Place {self.place.id}"


class Place(models.Model):
    id = models.AutoField(primary_key=True)
    place_objects = models.ForeignKey(
        "ObjectsInPlace", on_delete=models.CASCADE, related_name="places"
    )

    def __str__(self):
        return f"Place {self.id}"


class ObjectsInPlace(models.Model):
    id = models.AutoField(primary_key=True)
    chair = models.IntegerField()
    person = models.IntegerField()
    interactive_whiteboard = models.IntegerField()
    keyboard = models.IntegerField()
    monitor = models.IntegerField()
    pc = models.IntegerField()
    table = models.IntegerField()

    def __str__(self):
        return f"ObjectsInPlace {self.id}"


class EventHistory(models.Model):
    id = models.AutoField(primary_key=True)
    LINE_COUNTER_TYPES = (
        ("in", "in"),
        ("out", "out"),
    )
    type = models.CharField(max_length=3, choices=LINE_COUNTER_TYPES)
    date = models.DateTimeField()
    object = models.ForeignKey(
        Object, on_delete=models.CASCADE, related_name="event_objects"
    )

    def __str__(self):
        return f"Event {self.id} at {self.date}"

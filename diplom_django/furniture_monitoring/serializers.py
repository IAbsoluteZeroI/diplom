from rest_framework import serializers
from .models import EventHistory

class EventHistorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventHistory
        fields = ('id', 'frame', 'object', 'from_place', 'to_place')
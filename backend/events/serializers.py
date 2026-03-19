from rest_framework import serializers
from .models import Event


class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "category",
            "poster",
            "venue",
            "start_datetime",
            "end_datetime",
        ]


class EventSerializer(serializers.ModelSerializer):

    club_name = serializers.CharField(
        source="club.name",
        read_only=True
    )

    

    class Meta:
        model = Event
        fields = "__all__"
from rest_framework import serializers
from .models import Club
from users.models import User


class ClubCreateSerializer(serializers.ModelSerializer):

    organizer_id = serializers.IntegerField(required=False)

    class Meta:
        model = Club
        fields = [
            "id",
            "name",
            "description",
            "category",
            "image",
            "organizer_id"
        ]

    def create(self, validated_data):

        organizer_id = validated_data.pop("organizer_id", None)

        club = Club.objects.create(**validated_data)

        if organizer_id:

            try:

                user = User.objects.get(id=organizer_id)

                user.role = "ORGANIZER"
                user.club = club
                user.save()

                club.organizer = user
                club.save()

            except User.DoesNotExist:
                pass

        return club


class ClubSerializer(serializers.ModelSerializer):

    organizer_name = serializers.CharField(
        source="organizer.username",
        read_only=True
    )

    class Meta:
        model = Club
        fields = "__all__"
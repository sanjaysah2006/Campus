from rest_framework import serializers
from .models import User, StudentProfile
from datetime import datetime


class StudentRegisterSerializer(serializers.Serializer):

    name = serializers.CharField()
    roll_no = serializers.CharField()
    section = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    id_card = serializers.ImageField(required=False)

    def validate_roll_no(self, value):

        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Student with this roll number already exists."
            )

        return value


    def get_batch(self, roll):

        if roll.startswith("1123"):
            return "2023-27"

        if roll.startswith("1122"):
            return "2022-26"

        if roll.startswith("1124"):
            return "2024-28"

        return "Unknown"


    def calculate_semester(self, batch):

        if batch == "Unknown":
            return 1

        year = int(batch.split("-")[0])
        current_year = datetime.now().year

        semester = (current_year - year) * 2 + 1

        if semester < 1:
            semester = 1

        if semester > 8:
            semester = 8

        return semester


    def create(self, validated_data):

        name = validated_data["name"]
        roll = validated_data["roll_no"]

        batch = self.get_batch(roll)
        semester = self.calculate_semester(batch)

        user = User.objects.create_user(
            username=roll,
            email=validated_data["email"],
            password=validated_data["password"],
            role="STUDENT",
            first_name=name
        )

        StudentProfile.objects.create(
            user=user,
            name=name,
            roll_no=roll,
            course="B.Tech CSE",
            batch=batch,
            semester=semester,
            section=validated_data["section"],
            phone=validated_data["phone"],
            id_card=validated_data.get("id_card")
        )

        return user
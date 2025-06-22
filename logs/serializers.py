from rest_framework import serializers
from .models import Attendance, User
from datetime import datetime


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["user_id", "username"]


class AttendanceSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    username = serializers.CharField(write_only=True)

    class Meta:
        model = Attendance
        fields = [
            "id",
            "user",
            "username",
            "date",
            "arrival",
            "lunch_start",
            "lunch_end",
            "departure",
        ]
        read_only_fields = ["id"]

    def validate_username(self, value):
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError("User with this username does not exist.")
        return value

    def create(self, validated_data):
        username = validated_data.pop("username")
        user = User.objects.get(username=username)

        # Default to current date in dd-mm-yy format if not provided
        if "date" not in validated_data or not validated_data["date"]:
            validated_data["date"] = datetime.now().strftime("%d-%m-%y")

        return Attendance.objects.create(user=user, **validated_data)

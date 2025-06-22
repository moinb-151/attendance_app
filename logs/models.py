from django.db import models
import random


def generate_user_id():
    return str(random.randint(1000, 9999))


class User(models.Model):
    user_id = models.CharField(
        max_length=4, unique=True, default=generate_user_id, editable=False
    )
    username = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.username


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.CharField(max_length=10)  # Format: dd-mm-yy
    arrival = models.CharField(max_length=10, blank=True, null=True)
    lunch_start = models.CharField(max_length=10, blank=True, null=True)
    lunch_end = models.CharField(max_length=10, blank=True, null=True)
    departure = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        unique_together = ["user", "date"]

    def __str__(self):
        return f"{self.user.username} - {self.date}"

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from django.utils.timezone import timedelta
from .models import Attendance, User
from .serializers import AttendanceSerializer, UserSerializer
from django.utils import timezone
from datetime import datetime
import csv


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttendanceListCreateView(generics.ListCreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer


class AttendanceUpdateView(generics.UpdateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer


class AttendanceExportCSVView(APIView):
    def get(self, request):
        start_date = request.GET.get("start_date")  # dd-mm-yy
        end_date = request.GET.get("end_date")  # dd-mm-yy
        username = request.GET.get("username")

        if not start_date or not end_date:
            return HttpResponse("Missing 'start_date' or 'end_date'", status=400)

        try:
            start = datetime.strptime(start_date, "%d-%m-%y")
            end = datetime.strptime(end_date, "%d-%m-%y")
        except ValueError:
            return HttpResponse("Invalid date format. Use dd-mm-yy", status=400)

        filtered = Attendance.objects.filter(
            user__username=username,
            date__in=[
                (start + timedelta(days=i)).strftime("%d-%m-%y")
                for i in range((end - start).days + 1)
            ],
        )

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="attendance.csv"'

        writer = csv.writer(response)
        writer.writerow(
            ["Username", "Date", "Arrival", "Lunch Start", "Lunch End", "Departure"]
        )
        for entry in filtered:
            writer.writerow(
                [
                    entry.user.username,
                    entry.date,
                    entry.arrival or "",
                    entry.lunch_start or "",
                    entry.lunch_end or "",
                    entry.departure or "",
                ]
            )

        return response

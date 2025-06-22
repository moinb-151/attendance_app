from django.urls import path
from .views import *

urlpatterns = [
    path("user/register/", UserRegisterView.as_view(), name="user-register"),
    path("add-log/", AttendanceListCreateView.as_view(), name="add-log"),
    path("get-logs/", AttendanceListCreateView.as_view(), name="get-logs"),
    path("update-log/<int:pk>/", AttendanceUpdateView.as_view(), name="update-log"),
    path("export-csv/", AttendanceExportCSVView.as_view(), name="export-csv"),
]

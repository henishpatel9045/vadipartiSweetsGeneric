from django.urls import path

from .views import home, download_excel, AdminDashboardAPIView

urlpatterns = [
    path("", home),
    path("excel", download_excel, name="download-excel"),
    path("dashboard", AdminDashboardAPIView.as_view(), name="dashboard-data"),
]

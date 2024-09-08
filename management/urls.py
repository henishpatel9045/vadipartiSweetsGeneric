from django.urls import path

from .views import home, download_excel

urlpatterns = [
    path('', home),
    path('excel', download_excel, name="download-excel"),
]


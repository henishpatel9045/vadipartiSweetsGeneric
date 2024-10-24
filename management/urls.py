from django.urls import path

from .views import (
    home,
    download_excel,
    AdminDashboardAPIView,
    DepositPaymentFormTemplateView,
)

urlpatterns = [
    path("configuration", home),
    path("excel", download_excel, name="download-excel"),
    path("dashboard", AdminDashboardAPIView.as_view(), name="dashboard-data"),
    path(
        "payment-deposits",
        DepositPaymentFormTemplateView.as_view(),
        name="payment-deposit-form",
    ),
]

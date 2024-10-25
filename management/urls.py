from django.urls import path

from .views import (
    home,
    download_excel,
    AdminDashboardAPIView,
    DepositPaymentFormTemplateView,
    DepositPaymentAPIView,
)

urlpatterns = [
    path("configuration", home),
    path("excel", download_excel, name="download-excel"),
    path("dashboard", AdminDashboardAPIView.as_view(), name="dashboard-data"),
    path(
        "payment-deposits",
        DepositPaymentAPIView.as_view(),
        name="payment-deposit-api",
    ),
    path(
        "payment-deposits-form",
        DepositPaymentFormTemplateView.as_view(),
        name="payment-deposit-form",
    ),
]

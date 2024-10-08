from django.urls import path

from booking.views import (
    NewOrderTemplateView,
    CreateOrderView,
    EditOrderView,
    EditOrderTemplateView,
    UserBookingsTemplateView,
    deleteOrderView,
    OrdersPrintTemplateView,
    UserDashboardStatTemplateView,
    UserDepositsTemplateView,
    UserOrderDeliveryStatusTemplateView,
)


urlpatterns = [
    path("new-order/", NewOrderTemplateView.as_view(), name="new-order"),
    path("new-order/create/", CreateOrderView.as_view(), name="create-new-order"),
    path("order/<str:pk>", EditOrderTemplateView.as_view(), name="edit-order-template"),
    path("order/<str:pk>/edit/", EditOrderView.as_view(), name="edit-order"),
    path("order/<str:pk>/delete/", deleteOrderView, name="delete-order"),
    path("user/bookings", UserBookingsTemplateView.as_view(), name="user-bookings"),
    path("user/stats", UserDashboardStatTemplateView.as_view(), name="user-stats"),
    path("user/deposits", UserDepositsTemplateView.as_view(), name="user-deposits"),
    path("user/orders-delivery", UserOrderDeliveryStatusTemplateView.as_view(), name="user-order-delivery"),
    path("print", OrdersPrintTemplateView.as_view(), name="booking-print"),
]

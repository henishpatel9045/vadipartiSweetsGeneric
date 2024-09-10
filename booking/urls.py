from django.urls import path

from booking.views import NewOrderTemplateView, CreateOrderView, EditOrderView, EditOrderTemplateView, UserHomeTemplateView, UserBookingsTemplateView, deleteOrderView, TempAPI, OrdersPrintTemplateView


urlpatterns = [
    path("new-order/", NewOrderTemplateView.as_view(), name="new-order"),
    path("new-order/create/", CreateOrderView.as_view(), name="create-new-order"),
    path("order/<str:pk>", EditOrderTemplateView.as_view(), name="edit-order-template"),
    path("order/<str:pk>/edit/", EditOrderView.as_view(), name="edit-order"),
    path("order/<str:pk>/delete/", deleteOrderView, name="delete-order"),
    path("user/home", UserHomeTemplateView.as_view(), name="user-home"),
    path("user/bookings", UserBookingsTemplateView.as_view(), name="user-bookings"),
    path("print", OrdersPrintTemplateView.as_view(), name="booking-print"),
]

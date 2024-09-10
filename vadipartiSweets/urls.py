from django.contrib import admin
from django.urls import path, include

from booking.views import (
    admin_home_redirect,
    logout_view,
    AdminHomeTemplateView,
    AdminDashboardTemplateView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("home", admin_home_redirect),
    path("admin-home", AdminHomeTemplateView.as_view(), name="admin-home"),
    path(
        "admin-dashboard", AdminDashboardTemplateView.as_view(), name="admin-dashboard"
    ),
    path("logout", logout_view),
    path("bookings/", include("booking.urls")),
    path("management/", include("management.urls")),
]

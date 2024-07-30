from django.contrib import admin
from django.urls import path
from .views import HealthCheckView

urlpatterns = [
    path("health-check", HealthCheckView.as_view(), name="health-check"),
]

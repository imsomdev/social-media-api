from django.contrib import admin
from django.urls import path
from .views import HealthCheckView
from .users.views import SignUpView

urlpatterns = [
    path("health-check", HealthCheckView.as_view(), name="health-check"),
    path("signup", SignUpView.as_view(), name="signup"),
]

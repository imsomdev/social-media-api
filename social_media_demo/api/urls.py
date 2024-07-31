from django.contrib import admin
from django.urls import path
from .views import HealthCheckView
from .users.views import SentFriendRequestView, SignUpView

urlpatterns = [
    path("health-check", HealthCheckView.as_view(), name="health-check"),
    path("signup", SignUpView.as_view(), name="signup"),
    path(
        "send-friend-request",
        SentFriendRequestView.as_view(),
        name="send-friend-request",
    ),
]

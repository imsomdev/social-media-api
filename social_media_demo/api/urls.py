from django.contrib import admin
from django.urls import path
from .views import HealthCheckView
from .users.views import (
    AcceptFriendRequestView,
    CancelFriendRequestView,
    GetFriendRequestListView,
    SentFriendRequestView,
    SignUpView,
)

urlpatterns = [
    path("health-check", HealthCheckView.as_view(), name="health-check"),
    path("signup", SignUpView.as_view(), name="signup"),
    path(
        "friend-request/send",
        SentFriendRequestView.as_view(),
        name="send-friend-request",
    ),
    path(
        "friend-request/cancel",
        CancelFriendRequestView.as_view(),
        name="cancel-friend-request",
    ),
    path(
        "friend-request",
        GetFriendRequestListView.as_view(),
        name="cancel-friend-request",
    ),
    path(
        "friend-request/accept",
        AcceptFriendRequestView.as_view(),
        name="accept-friend-request",
    ),
]

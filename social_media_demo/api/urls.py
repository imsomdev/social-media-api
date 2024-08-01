from django.contrib import admin
from django.urls import path
from .views import HealthCheckView
from .users.views import (
    CancelFriendRequestView,
    FriendRequestActionView,
    GetFriendListView,
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
        "friend-request/actions",
        FriendRequestActionView.as_view(),
        name="actions-friend-request",
    ),
    path(
        "friend-list",
        GetFriendListView.as_view(),
        name="friend-list",
    ),
]

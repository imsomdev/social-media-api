from django.contrib import admin
from django.urls import path
from .posts.views import CreatePostView, DeletePostView
from .views import HealthCheckView
from .users.views import (
    CancelFriendRequestView,
    FriendRequestActionView,
    GetAllUserView,
    GetFriendListView,
    GetFriendRequestListView,
    LoginView,
    SentFriendRequestView,
    SignUpView,
)

urlpatterns = [
    path("health-check", HealthCheckView.as_view(), name="health-check"),
    path("signup", SignUpView.as_view(), name="signup"),
    path("login", LoginView.as_view(), name="login"),
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
        name="friend-request",
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
    path("all-users", GetAllUserView.as_view(), name="all-users"),
    path("create-post", CreatePostView.as_view(), name="create-post"),
    path("delete-post", DeletePostView.as_view(), name="delete-post"),
]

from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

from api.models import FriendRequest
from .serializers import (
    GetSentFriendRequestSerializer,
    SentFriendRequestSerializer,
    SignUpSerializer,
)


class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(
                    {"message": "Registration successful"},
                    status=201,
                )
            except IntegrityError:
                return Response(
                    {"error": "A user with this username or email already exists"},
                    status=400,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=400)
        return Response(serializer.errors, status=400)


class SentFriendRequestView(APIView):
    def post(self, request):
        serializer = SentFriendRequestSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "friend request send successfully"}, status=201)
        return Response(serializer.errors, status=400)

    def get(self, request):
        user = "012ce81a-e10e-4e90-b45c-01945171daf0"
        sent_requests = FriendRequest.objects.filter(
            from_user=user,
            status="pending",
        )
        serializer = GetSentFriendRequestSerializer(sent_requests, many=True)
        return Response(
            {"count": sent_requests.count(), "friend_requests": serializer.data},
            status=200,
        )


class CancelFriendRequestView(APIView):
    def post(self, request):
        try:
            friend_request = FriendRequest.objects.get(
                to_user=request.data.get("to_user"),
                from_user=request.data.get("from_user"),
            )
            if friend_request.status == "pending":
                friend_request.status = "cancelled"
                friend_request.save()
                return Response({"message": "Friend request cancelled."}, status=200)
            else:
                return Response(
                    {"error": "Cannot cancel a non-pending friend request."}, status=400
                )
        except FriendRequest.DoesNotExist:
            return Response({"error": "Friend request not found."}, status=404)

from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

from api.models import FriendRequest
from .serializers import SentFriendRequestSerializer, SignUpSerializer


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
        serializer = SentFriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def get(self, request):
        user = request.user
        sent_requests = FriendRequest.objects.filter(from_user=user)
        serializer = SentFriendRequestSerializer(sent_requests, many=True)
        return Response(
            {"count": sent_requests.count(), "friend_requests": serializer.data},
            status=200,
        )

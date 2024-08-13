from rest_framework_simplejwt.tokens import RefreshToken
from django.db import IntegrityError
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from api.models import CustomUser, FriendRequest
from .serializers import (
    CancelFriendRequestSerializer,
    FriendRequestActionSerializer,
    GetFriendRequestSerializer,
    GetSentFriendRequestSerializer,
    LoginSerializer,
    SentFriendRequestSerializer,
    SignUpSerializer,
    UserSerializer,
)
from django.db.models import Q


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


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]

            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response(
                {
                    "message": "Logged in successfully",
                    "jwt": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    },
                },
                status=200,
            )
        return Response(serializer.errors, status=400)


class SentFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SentFriendRequestSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Friend request sent successfully"}, status=201)
        return Response(serializer.errors, status=400)

    def get(self, request):
        user = request.user
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
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            serializer = CancelFriendRequestSerializer(
                data=request.data,
                context={"request": request},
            )
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Friend request cancelled."}, status=200)
            return Response(serializer.errors, status=400)
        except FriendRequest.DoesNotExist:
            return Response({"error": "Friend request not found."}, status=404)


class GetFriendRequestListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        received_requests = FriendRequest.objects.filter(
            to_user=user,
            status="pending",
        )
        serializer = GetFriendRequestSerializer(received_requests, many=True)
        return Response(
            {"count": received_requests.count(), "friend_requests": serializer.data},
            status=200,
        )


class FriendRequestActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = FriendRequestActionSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            action = serializer.validated_data["action"]
            return Response(
                {"message": f"Friend request {action}ed successfully"}, status=200
            )

        return Response(serializer.errors, status=400)


class GetFriendListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get all accepted friend requests where the current user is either from_user or to_user
        sent_friends = FriendRequest.objects.filter(from_user=user, status="accepted")
        received_friends = FriendRequest.objects.filter(to_user=user, status="accepted")

        # Combine the friends from both queries, ensuring no duplicates
        friend_users = set(
            [friend.to_user for friend in sent_friends]
            + [friend.from_user for friend in received_friends]
        )

        # Serialize the friend user objects
        serializer = UserSerializer(friend_users, many=True)

        return Response(serializer.data, status=200)


class GetAllUserView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        friends = FriendRequest.objects.filter(
            (Q(from_user=user) | Q(to_user=user)) & Q(status="accepted")
        ).values_list("from_user", "to_user")
        friend_ids = {user_id for friend_pair in friends for user_id in friend_pair}
        pending_requests = FriendRequest.objects.filter(
            (Q(from_user=user) | Q(to_user=user)) & Q(status="pending")
        ).values_list("from_user", "to_user")
        pending_ids = {
            user_id for pending_pair in pending_requests for user_id in pending_pair
        }
        exclude_ids = friend_ids.union(pending_ids)
        return CustomUser.objects.exclude(id__in=exclude_ids).exclude(id=user.id)

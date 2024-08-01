from rest_framework import serializers
import re
from api.models import CustomUser, FriendRequest
from django.db.models import Q


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "first_name", "last_name"]


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    confirm_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
            "confirm_password",
        ]

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        return value

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError(
                "Password must be at least 6 characters long."
            )
        if not re.search(r"\d", value):
            raise serializers.ValidationError(
                "Password must contain at least one digit."
            )
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError(
                "Password must contain at least one special character."
            )
        return value

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = CustomUser.objects.create(
            username=validated_data["username"].lower(),
            email=validated_data["email"].lower(),
            first_name=validated_data.get("first_name", "").lower(),
            last_name=validated_data.get("last_name", "").lower(),
        )
        user.set_password(validated_data["password"].lower())
        user.save()
        return user


class SentFriendRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendRequest
        fields = ["from_user", "to_user", "status"]

    def validate(self, data):
        from_user = data.get("from_user")
        to_user = data.get("to_user")

        if from_user == to_user:
            raise serializers.ValidationError(
                "You cannot send a friend request to yourself."
            )

        if FriendRequest.objects.filter(
            Q(from_user=from_user, to_user=to_user, status="accepted")
            | Q(to_user=from_user, from_user=to_user, status="accepted")
        ).exists():
            raise serializers.ValidationError("Already friends.")

        if (
            FriendRequest.objects.filter(from_user=from_user, to_user=to_user)
            .exclude(Q(status="cancelled") | Q(status="rejected"))
            .exists()
        ):
            raise serializers.ValidationError(
                "Friend request already sent to this user."
            )

        if (
            FriendRequest.objects.filter(from_user=to_user, to_user=from_user)
            .exclude(Q(status="cancelled") | Q(status="rejected"))
            .exists()
        ):
            raise serializers.ValidationError(
                "This user has already sent you a friend request."
            )

        return data

    def create(self, validated_data):
        from_user = validated_data.get("from_user")
        to_user = validated_data.get("to_user")

        # Check if a friend request already exists (including cancelled ones)
        existing_request = FriendRequest.objects.filter(
            from_user=from_user, to_user=to_user
        ).first()

        if existing_request:
            # If it exists, update the status to "pending" or as appropriate
            existing_request.status = "pending"
            existing_request.save()
            return existing_request
        else:
            # If no existing request, create a new one
            friend_request = FriendRequest.objects.create(
                from_user=from_user,
                to_user=to_user,
                status="pending",
            )
            return friend_request


class GetSentFriendRequestSerializer(serializers.ModelSerializer):
    to_user = UserSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ["to_user", "status"]


class GetFriendRequestSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ["from_user", "status"]


class CancelFriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ["from_user", "to_user", "status"]

    def validate(self, data):
        from_user = data.get("from_user")
        to_user = data.get("to_user")
        friend_request = FriendRequest.objects.get(
            to_user=to_user,
            from_user=from_user,
        )
        if friend_request.status != "pending":
            raise serializers.ValidationError(
                "Cannot cancel a non-pending friend request"
            )
        return data

    def create(self, validated_data):
        from_user = validated_data.get("from_user")
        to_user = validated_data.get("to_user")
        existing_request = FriendRequest.objects.filter(
            from_user=from_user, to_user=to_user
        ).first()

        if existing_request:
            existing_request.status = "cancelled"
            existing_request.save()
            return existing_request


class FriendRequestActionSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(write_only=True)
    action = serializers.ChoiceField(choices=["accept", "reject"], write_only=True)

    def validate(self, data):
        user_id = data.get("user_id")
        action = data.get("action")
        current_user = "012ce81a-e10e-4e90-b45c-01945171daf0"

        if action not in ["accept", "reject"]:
            raise serializers.ValidationError(
                "Invalid action. Must be 'accept' or 'reject'."
            )

        try:
            friend_request = FriendRequest.objects.get(
                from_user_id=user_id, to_user=current_user, status="pending"
            )
        except FriendRequest.DoesNotExist:
            raise serializers.ValidationError(
                "No pending friend request found from this user."
            )

        return data

    def save(self):
        user_id = self.validated_data["user_id"]
        action = self.validated_data["action"]
        current_user = "012ce81a-e10e-4e90-b45c-01945171daf0"

        try:
            friend_request = FriendRequest.objects.get(
                from_user_id=user_id, to_user=current_user, status="pending"
            )
        except FriendRequest.DoesNotExist:
            raise serializers.ValidationError("No pending friend request found.")

        if action == "accept":
            friend_request.status = "accepted"
            friend_request.save()
        elif action == "reject":
            friend_request.status = "rejected"
            friend_request.save()

        return friend_request

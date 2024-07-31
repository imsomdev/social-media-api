from rest_framework import serializers
from django.core.exceptions import ValidationError
import re
from api.models import CustomUser, FriendRequest


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

        # Prevent self-friend requests
        if from_user == to_user:
            raise serializers.ValidationError(
                "You cannot send a friend request to yourself."
            )

        # Check if a friend request already exists from from_user to to_user
        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            raise serializers.ValidationError(
                "Friend request already sent to this user."
            )

        # Check if a friend request already exists from to_user to from_user (reverse direction)
        if FriendRequest.objects.filter(from_user=to_user, to_user=from_user).exists():
            raise serializers.ValidationError(
                "This user has already sent you a friend request."
            )

        # Additional validations as needed...

    def create(self, validated_data):
        friend_request = FriendRequest.objects.create(
            from_user=validated_data.get("from_user"),
            to_user=validated_data.get("to_user"),
            status="pending",
        )

        return friend_request

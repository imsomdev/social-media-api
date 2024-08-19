from rest_framework import serializers
from api.models import PostModel


class PostSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = PostModel
        fields = [
            "id",
            "user",
            "username",
            "caption",
            "image",
            "comments_count",
            "likes_count",
            "shares_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "user",
            "comments_count",
            "likes_count",
            "shares_count",
            "created_at",
            "updated_at",
        ]

    def get_username(self, obj):
        return obj.user.username

    def validate(self, data):
        caption = data.get("caption")
        image = data.get("image")

        if not caption and not image:
            raise serializers.ValidationError(
                "Either caption or image must be provided."
            )

        return data

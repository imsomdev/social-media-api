from rest_framework import serializers
from api.models import Post, Like, Comment, Share


class PostSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "user",
            "username",
            "caption",
            "is_liked_by_user",
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

    def get_is_liked_by_user(self, obj):
        # Ensure the user is passed in context
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        user = request.user
        return Like.objects.filter(post=obj, user=user).exists()

    def validate(self, data):
        caption = data.get("caption")
        image = data.get("image")

        if not caption and not image:
            raise serializers.ValidationError(
                "Either caption or image must be provided."
            )

        return data


class PostCommentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "text",
            "post",
            "username",
        ]

    def get_username(self, obj):  # Corrected the method name
        return obj.user.username

    def create(self, validated_data):
        user = self.context["request"].user
        post = validated_data.get("post")  # This is already a Post instance
        text = validated_data.get("text")

        # Create and return the Comment instance
        comment = Comment.objects.create(
            user=user,
            post=post,
            text=text,
        )
        return comment

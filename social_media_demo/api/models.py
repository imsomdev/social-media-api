import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class FriendRequest(models.Model):
    from_user = models.ForeignKey(
        CustomUser, related_name="sent_requests", on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        CustomUser, related_name="received_requests", on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


from django.db import models


class PostModel(models.Model):
    user = models.ForeignKey(CustomUser, related_name="posts", on_delete=models.CASCADE)
    caption = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True)  # Ensure this line exists
    comments_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post by {self.user.username} - {self.caption[:30]}"

    def increment_comments_count(self):
        self.comments_count += 1
        self.save()

    def increment_shares_count(self):
        self.shares_count += 1
        self.save()

    def increment_likes_count(self):
        self.likes_count += 1
        self.save()


class CommentModel(models.Model):
    post = models.ForeignKey(
        PostModel, related_name="comments", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        CustomUser, related_name="comments", on_delete=models.CASCADE
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.id}"


class ShareModel(models.Model):
    post = models.ForeignKey(PostModel, related_name="shares", on_delete=models.CASCADE)
    user = models.ForeignKey(
        CustomUser, related_name="shares", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Share by {self.user.username} on {self.post.id}"


class LikeModel(models.Model):
    post = models.ForeignKey(PostModel, related_name="likes", on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, related_name="likes", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like by {self.user.username} on {self.post.id}"

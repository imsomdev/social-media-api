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

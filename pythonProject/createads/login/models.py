from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
import uuid


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    groups = models.ManyToManyField(Group, related_name='user_set_custom', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='user_set_custom', blank=True)
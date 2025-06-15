from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    discord_id = models.CharField(
        max_length=20, unique=True, null=True, blank=True
    )
    discord_username = models.CharField(max_length=32, null=True, blank=True)
    avatar_url = models.URLField(null=True, blank=True)

# users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Add custom fields if needed, e.g.:
    is_tenant = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

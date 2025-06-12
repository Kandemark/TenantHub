# users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Includes additional fields and utility methods for tenant management.
    """
    is_tenant = models.BooleanField(default=False, help_text="Designates whether the user is a tenant.")
    is_admin = models.BooleanField(default=False, help_text="Designates whether the user is an admin.")
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="User's phone number.")
    date_of_birth = models.DateField(blank=True, null=True, help_text="User's date of birth.")
    address = models.CharField(max_length=255, blank=True, null=True, help_text="User's address.")
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, help_text="Profile picture.")
    email_verified = models.BooleanField(default=False, help_text="Indicates if the user's email is verified.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Account creation timestamp.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last profile update timestamp.")

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        """
        Returns the user's full name.
        """
        return f"{self.first_name} {self.last_name}".strip()

    def age(self):
        """
        Returns the user's age in years, if date_of_birth is set.
        """
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    def get_profile_picture_url(self):
        """
        Returns the URL of the user's profile picture, or a default if not set.
        """
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/images/default_profile.png'

    def verify_email(self):
        """
        Marks the user's email as verified.
        """
        self.email_verified = True
        self.save(update_fields=['email_verified'])

    def is_profile_complete(self):
        """
        Checks if the user's profile is complete.
        """
        required_fields = [self.first_name, self.last_name, self.email, self.phone_number, self.address]
        return all(required_fields)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at']


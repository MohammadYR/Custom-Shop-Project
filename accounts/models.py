from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import BaseModel


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    is_seller = models.BooleanField(default=False)
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username

class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=120, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    def __str__(self):
        return self.full_name

class Address(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    line1 = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    purpose = models.CharField(max_length=20, default="shipping") # shipping/billing

    class Meta:
        constraints = [
            # One live default address per user; soft-deleted rows are ignored.
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(is_default=True, deleted_at__isnull=True),
                name="unique_default_address_per_user",
            )
        ]

class OTP(BaseModel):
    PURPOSES = [
    ("login", "Login"),
    ("register", "Register"), 
    ("reset_password", "Reset Password"),
    ("verify_phone", "Verify Phone"),
    ("verify_email", "Verify Email"),
]
    channel = models.CharField(max_length=10, default="sms") # sms/email
    target = models.CharField(max_length=120) # phone or email
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSES)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    # Number of wrong codes submitted for this OTP (brute-force protection).
    attempts = models.PositiveSmallIntegerField(default=0)


    class Meta:
        indexes = [models.Index(fields=["target","purpose","expires_at"])]
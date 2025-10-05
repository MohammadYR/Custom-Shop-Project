from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import BaseModel
import uuid


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    is_seller = models.BooleanField(default=False)
    USERNAME_FIELD = "username" 
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


    class Meta:
        indexes = [models.Index(fields=["target","purpose","expires_at"])]
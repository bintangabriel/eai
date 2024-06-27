from django.db import models
from django.contrib.auth.models import AbstractUser

class UserProfile(AbstractUser):
    no_telp = models.CharField(max_length=50, null=False, default="000")
    profile_picture = models.ImageField(upload_to='images/', blank=True)


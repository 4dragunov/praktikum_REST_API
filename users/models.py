from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from django.db import models


class UserRole(models.TextChoices):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'


class User(AbstractUser):
    """Расширение стандартной модели пользователя Django"""
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=False, unique=True,
                              validators=[validate_email, ])
    role = models.CharField(
        max_length=50, blank=False, choices=UserRole.choices,
        default=UserRole.USER
    )
    secret = models.CharField(max_length=20)
    username = models.CharField(max_length=50,
                                blank=True,
                                null=True,
                                unique=True,
                                db_index=True)

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Кастомная модель пользователя."""
    ROLES = [
        ("user", "Пользователь"),
        ("admin", "Администратор"),
        ("moderator", "Модератор"),
    ]

    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(max_length=254, unique=True)
    role = models.CharField(
        max_length=15,
        choices=ROLES,
        default="user",
        verbose_name="Роль пользователя",
    )
    bio = models.TextField(verbose_name="Биография", blank=True)
    updated_at = models.DateTimeField(default=timezone.now)

    @property
    def is_user(self):
        return self.role == self.ROLES[0][0]

    @property
    def is_admin(self):
        return self.role == self.ROLES[1][0]

    @property
    def is_moderator(self):
        return self.role == self.ROLES[2][0]

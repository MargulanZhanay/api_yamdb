from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLES = [
        ('user', 'Пользователь'),
        ('admin', 'Администратор'),
        ('moderator', 'Модератор'),
    ]

    username = models.CharField(max_length=150,
                                blank=False,
                                null=False,
                                unique=True)
    email = models.EmailField(blank=False,
                              null=False,
                              unique=True)
    role = models.CharField(max_length=15,
                            choices=ROLES,
                            default='user',
                            verbose_name='Роль пользователя',
                            )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
        )

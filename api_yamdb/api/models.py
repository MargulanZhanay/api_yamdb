from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None):
        """ Создает и возвращает пользователя с имэйлом, паролем и именем. """
        if username is None:
            raise TypeError('Поле username обязательно.')

        if email is None:
            raise TypeError('Поле email обязательно.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        """ Создает и возвращет пользователя с привилегиями суперадмина. """
        if password is None:
            raise TypeError('Суперадмин должен иметь пароль.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLES = [
        ('user', 'Пользователь'),
        ('admin', 'Администратор'),
        ('moderator', 'Модератор'),
    ]

    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=15,
                            choices=ROLES,
                            default='user',
                            verbose_name='Роль пользователя',
                            )
    bio = models.TextField(verbose_name='Биография', blank=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()


class EmailConfirmation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='confirm',
        verbose_name='Пользователь'
    )
    confirmation_code = models.CharField(max_length=10)
    confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

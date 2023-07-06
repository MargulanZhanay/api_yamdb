from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from .validators import year_validator  # isort: skip


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None, confirmation_code=None, *args, **kwargs):
        """Создает и возвращает пользователя с имэйлом, паролем и именем."""
        if username is None:
            raise TypeError('Поле username обязательно.')

        if email is None:
            raise TypeError('Поле email обязательно.')

        user = self.model(username=username, email=self.normalize_email(email), confirmation_code=confirmation_code)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        """Создает и возвращет пользователя с привилегиями суперадмина."""
        if password is None:
            raise TypeError('Суперадмин должен иметь пароль.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Базовая модель пользователя."""
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
    confirmation_code = models.CharField(max_length=10, blank=True, null=True)
    confirmed = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()


class Category(models.Model):
    name = models.CharField(
        'Название категории',
        max_length=256
    )
    slug = models.SlugField(
        'Слаг категории',
        max_length=50,
        db_index=True,
        unique=True
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.slug


class Genre(models.Model):
    name = models.CharField(
        'Название жанра',
        max_length=256
    )
    slug = models.SlugField(
        'Слаг жанра',
        max_length=50,
        db_index=True,
        unique=True
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self) -> str:
        return self.slug


class Title(models.Model):
    name = models.CharField(
        'Название произведения',
        max_length=256,
        db_index=True
    )
    year = models.IntegerField(
        'Год выпуска',
        validators=[year_validator]
    )
    description = models.TextField(
        'Описание',
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр произведения',
        blank=False,
        related_name='titles',

    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория произведения',
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name='titles'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f'{self.title} {self.genre}'


class Review(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    score = models.IntegerField(
        'Оценка от 1 до 10',
        validators=[MaxValueValidator(10),
                    MinValueValidator(1)]
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            ),
        ]

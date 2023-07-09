"""Сериализаторы приложения api."""
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from reviews.models import Category, Comments, Genre, Review, Title, User

from .utils import generate_short_hash_mm3


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('id',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('id',)
        model = Genre


class TitleGetSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )

    class Meta:
        model = Title
        fields = '__all__'


class TitlePostSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=['title', 'author']
            )
        ]


class CommentsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comments."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comments


class RegistrationSerializer(serializers.ModelSerializer):
    """Сериализация регистрации пользователя и создания нового."""
    username = serializers.CharField(
        max_length=150,
        validators=[RegexValidator(r'^[\w.@+-]+\Z$', 'Некорректный формат.')])
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username', 'email')

    def create(self, validated_data):
        return User.objects.update_or_create(**validated_data)

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        # Проверка запрещенных имен пользователя
        if username in settings.BANNED_USERNAMES:
            message = f'Имя пользователя {username} запрещено.'
            raise serializers.ValidationError(
                {'message': message})

        # Проверка занятости email другим пользователем
        user = User.objects.filter(email=email)
        if user.exists() and user[0].username != username:
            raise serializers.ValidationError(
                {'message':
                 f'Данный email={email} занят другим пользователем.'})

        # Проверка соответствия email пользователю
        user = User.objects.filter(username=username)
        if user.exists() and user[0].email != email:
            raise serializers.ValidationError(
                {'message':
                 f'У пользователя {user[0]} другой email.'})

        return data


class ConfirmRegistrationSerializer(serializers.ModelSerializer):
    """Подтверждение регистрации."""
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def validate(self, data):
        username = data.get('username')
        user = get_object_or_404(User, username=username)
        confirmation_code = data.get('confirmation_code')

        # Если код невалидный выбрасываем исключение
        code = generate_short_hash_mm3(
            f'{user.username}{user.email}{user.updated_at}')
        if code != confirmation_code:
            raise serializers.ValidationError(
                {'message': 'Некорректный код.'})

        return {'username': user,
                'confirmation_code': confirmation_code}


class UserSerializer(serializers.ModelSerializer):
    """Получает пользователей списокм или создает нового."""
    username = serializers.CharField(
        max_length=150,
        validators=[RegexValidator(r'^[\w.@+-]+\Z$', 'Некорректный формат.')])

    class Meta:
        model = User
        fields = ('username', 'email',
                  'first_name', 'last_name',
                  'bio', 'role')

    def validate(self, data):
        username = data.get('username')

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {'message':
                 'Пользователь уже существует.'})

        return data

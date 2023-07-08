"""Сериализаторы приложения api."""
from django.conf import settings
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .utils import generate_short_hash_mm3

from reviews.models import Review, User  # isort: skip


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        total_score = sum(review.score for review in reviews)
        rating = total_score / len(reviews)
        return rating


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.PrimaryKeyRelatedField(read_only=True)
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = '__all__'
        model = Review
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=['title', 'author']
            )
        ]


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


class UserListCreateSerializer(serializers.ModelSerializer):
    """Получает пользователей списокм или создает нового."""

    class Meta:
        model = User
        fields = ('username', 'email',
                  'first_name', 'last_name',
                  'bio', 'role')

"""Сериализаторы приложения api."""
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.validators import UniqueTogetherValidator

from .exceptions import CustomValidation

from reviews.models import Review, EmailConfirmation, User  # isort: skip


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

    class Meta:
        model = User
        fields = ('username', 'email')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def validate(self, data):
        """Проверка запрещенных имен пользователя."""
        username = data.get('username')
        if username in settings.BANNED_USERNAMES:
            message = f'Имя пользователя {username} запрещено.'
            raise serializers.ValidationError(
                {'message': message})
        return data


class ConfirmRegistrationSerializer(serializers.ModelSerializer):
    """Подтверждение регистрации."""
    username = serializers.SlugRelatedField(slug_field='username',
                                            queryset=User.objects.all())

    class Meta:
        model = EmailConfirmation
        fields = ('username', 'confirmation_code')

    def to_internal_value(self, data):
        username = data.get('username')
        user = User.objects.filter(username=username)
        if not user.exists():
            message = f'Пользователь {username} не существует.'
            raise CustomValidation(message,
                                   username,
                                   status.HTTP_404_NOT_FOUND)
        data['username'] = user[0]
        return data

    def validate(self, data):
        user = data.get('username')
        confirmation_code = data.get('confirmation_code')

        # Если код невалидный выбрасываем исключение
        try:
            user.confirm.get(confirmation_code=confirmation_code)
        except EmailConfirmation.DoesNotExist:
            raise serializers.ValidationError(
                {'message': 'Некорректный код.'})

        return data

    def update(self, instance, validated_data):
        instance.confirmed = True
        instance.save()
        return instance

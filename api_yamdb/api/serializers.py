"""Сериализаторы приложения api."""
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.validators import UniqueTogetherValidator

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
    """Сериализатор регистрации пользователя."""

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, data):
        """Проверка запрещенных имен пользователя."""
        username = data.get('username')
        if username in settings.BANNED_USERNAMES:
            message = f'Имя пользователя {username} запрещено.'
            raise serializers.ValidationError(
                {'message': message})
        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data, code):
        instance.confirmation_code = code
        instance.save()
        return instance


class ConfirmRegistrationSerializer(serializers.ModelSerializer):
    """Подтверждение регистрации."""

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def validate(self, data):
        user = data.get('username')
        confirmation_code = data.get('confirmation_code')

        # # Если код невалидный выбрасываем исключение
        # try:
        #     user.confirm.get(confirmation_code=confirmation_code)
        # except EmailConfirmation.DoesNotExist:
        #     raise serializers.ValidationError(
        #         {'message': 'Некорректный код.'}, code=404)

        return data

    def update(self, instance, validated_data):
        instance.confirmed = True
        instance.save()
        return instance

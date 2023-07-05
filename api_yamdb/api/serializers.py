"""Сериализаторы приложения api."""
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import EmailConfirmation, User  # isort: skip
from reviews.models import Review  # isort: skip


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


class ConfirmRegistrationSerializer(serializers.ModelSerializer):
    """Подтверждение регистрации."""

    class Meta:
        model = EmailConfirmation
        fields = ('user', 'confirmation_code')

    def validate(self, data):
        user = get_object_or_404(User, username=data.get('user'))
        confirmation_code = data.get('confirmation_code')

        # Если код невалидный выбрасываем исключение
        try:
            user.confirm.get(confirmation_code=confirmation_code)
        except EmailConfirmation.DoesNotExist:
            raise serializers.ValidationError(
                {'message': 'Некорректный код.'})

        return data

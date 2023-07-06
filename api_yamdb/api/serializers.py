"""Сериализаторы приложения api."""
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import EmailConfirmation, User
from reviews.models import Genre, Title, Category, Review


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
    rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'

    def get_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        total_score = sum(review.score for review in reviews)
        rating = total_score / len(reviews)
        return rating


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
        user = User.objects.create_user(**validated_data)
        email = validated_data.get('email')
        code = get_random_string(10)

        # Сохранение кода подтверждения в базе данных
        EmailConfirmation.objects.create(user=user,
                                         confirmation_code=code)

        # Отправка письма с кодом подтверждения
        subject = 'Подтверждение регистрации'
        message = f'Код для подтверждения регистрации: {code}'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        return user


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
            print(f'confirmation_code: {confirmation_code}')
        except EmailConfirmation.DoesNotExist:
            raise serializers.ValidationError(
                {'message': 'Некорректный код.'})

        return data

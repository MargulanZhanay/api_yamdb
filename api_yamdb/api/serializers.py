"""Сериализаторы приложения api."""
from django.conf import settings
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from rest_framework import serializers

from .models import EmailConfirmation, User


class RegistrationSerializer(serializers.ModelSerializer):
    """ Сериализация регистрации пользователя и создания нового. """

    class Meta:
        model = User
        fields = ('username', 'email')

    def create(self, validated_data):
        email = validated_data.get('email')
        code = get_random_string(10)

        # Сохранение кода подтверждения в базе данных
        EmailConfirmation.objects.create(email=email, code=code)

        # Отправка письма с кодом подтверждения
        subject = 'Подтверждение регистрации'
        message = f'Код для подтверждения регистрации: {code}'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        return User.objects.create_user(**validated_data)

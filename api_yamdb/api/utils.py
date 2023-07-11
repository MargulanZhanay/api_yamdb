import mmh3
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.viewsets import GenericViewSet


class CategoryGenreMixinSet(CreateModelMixin, DestroyModelMixin,
                            ListModelMixin, GenericViewSet):
    pass


def send_email_confirm(email: str, code: str) -> None:
    """Отправка кода подтверждения на email."""

    subject = 'Подтверждение регистрации'
    message = f'Код для подтверждения регистрации: {code}'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


def generate_short_hash_mm3(data: str) -> str:
    """ Получает строку из полей username + email + updated_at,
        добавляет к ней SECRET_KEY, генерирует короткий хеш.
    """
    data += settings.SECRET_KEY
    hash_value = mmh3.hash(data)
    return str(abs(hash_value))

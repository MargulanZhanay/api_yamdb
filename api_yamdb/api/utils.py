from django.conf import settings
from django.core.mail import send_mail


def send_email_confirm(user: str, email: str, code: str) -> None:
    """Отправка кода подтверждения на email."""

    subject = 'Подтверждение регистрации'
    message = f'Код для подтверждения регистрации: {code}'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

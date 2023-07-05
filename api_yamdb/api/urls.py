"""Маршруты приложения api."""
from django.conf import settings
from django.urls import path

from .views import ConfirmationEmailAPIView, RegistrationAPIView

# Версия API
API_VERSION = settings.API_VERSION


urlpatterns = [
    path(f'{API_VERSION}/auth/signup/', RegistrationAPIView.as_view()),
    path(f'{API_VERSION}/auth/token/', ConfirmationEmailAPIView.as_view())
]

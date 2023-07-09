"""Маршруты приложения api."""
from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (ConfirmationEmailAPIView, RegistrationAPIView,
                    ReviewViewSet, UserViewSet)

# Версия API
API_VERSION = settings.API_VERSION

router = DefaultRouter()
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register('users', UserViewSet, basename='user')


urlpatterns = [
    path(f'{API_VERSION}/', include(router.urls)),
    path(f'{API_VERSION}/auth/signup/', RegistrationAPIView.as_view()),
    path(f'{API_VERSION}/auth/token/', ConfirmationEmailAPIView.as_view())
]

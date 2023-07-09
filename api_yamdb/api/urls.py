"""Маршруты приложения api."""
from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentsViewSet, ConfirmationEmailAPIView,
                    GenreViewSet, RegistrationAPIView, ReviewViewSet,
                    TitleViewSet, UserViewSet)

# Версия API
API_VERSION = settings.API_VERSION

router = DefaultRouter()
router.register(
    'categories',
    CategoryViewSet,
    basename='categories'
)
router.register(
    'genres',
    GenreViewSet,
    basename='genres'
)
router.register(
    'titles',
    TitleViewSet,
    basename='titles'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='comments'
)
router.register('users', UserViewSet, basename='user')
router.register('users/me', UserViewSet, basename='me')

urlpatterns = [
    path(f'{API_VERSION}/', include(router.urls)),
    path(f'{API_VERSION}/auth/signup/', RegistrationAPIView.as_view()),
    path(f'{API_VERSION}/auth/token/', ConfirmationEmailAPIView.as_view())
]

"""Вьюхи приложения api."""
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api.filters import TitleFitler
from api.permissions import IsAdmin, IsRedactor, Me, ReadOnly
from api.serializers import (CategorySerializer, CommentsSerializer,
                             ConfirmRegistrationSerializer, GenreSerializer,
                             MeSerializer, RegistrationSerializer,
                             ReviewSerializer, TitleGetSerializer,
                             TitlePostSerializer, UserSerializer)
from api.utils import (CategoryGenreMixinSet, generate_short_hash_mm3,
                       send_email_confirm)
from reviews.models import Review
from titles.models import Category, Genre, Title
from users.models import User


class RegistrationAPIView(APIView):
    """Создает нового пользователя. Отправляет код подтверждения."""
    permission_classes = (AllowAny,)

    def post(self, request):
        """Создаем или обновялем пользователя с текущим временем
        в поле updated_at, которое затем используется для генерации
        кода подтверждения.
        """
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, created = serializer.save(defaults={"updated_at": timezone.now})

        code = generate_short_hash_mm3(
            f"{user.username}{user.email}{user.updated_at}"
        )

        # Отправка кода на email
        send_email_confirm(user.email, code)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ConfirmationEmailAPIView(APIView):
    """Подтверждает регистрацию пользователя. Обновляет токен"""
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ConfirmRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get("username")
        # Обновляем дату, чтобы сделать код невалидным
        user.updated_at = timezone.now()
        user.save()

        token = str(RefreshToken.for_user(user).access_token)

        return Response({"token": token}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """Позволяет выполнить все операции CRUD с пользователями."""
    http_method_names = ("get", "post", "patch", "delete")
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "username"
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)


class MeRetrieveUpdateAPIView(APIView):
    """Пользователь может получить свои данные и поменять их."""
    permission_classes = (Me,)

    def get(self, request):
        user = request.user
        serializer = MeSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, format=None):
        user = request.user
        serializer = MeSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class GenreViewSet(CategoryGenreMixinSet):
    """Вьюсет жанр."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [ReadOnly | IsAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ("name",)
    lookup_field = "slug"


class CategoryViewSet(CategoryGenreMixinSet):
    """Вьюсет категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ReadOnly | IsAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ("name",)
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет произведений."""
    queryset = Title.objects.annotate(rating=Avg("reviews__score"))
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFitler
    permission_classes = [ReadOnly | IsAdmin]
    http_method_names = ("get", "post", "patch", "delete")

    def get_serializer_class(self):
        serializer_classes = {
            "create": TitlePostSerializer,
            "update": TitlePostSerializer,
            "partial_update": TitlePostSerializer,
        }
        default_serializer = TitleGetSerializer
        return serializer_classes.get(self.action, default_serializer)


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет отзывов."""
    http_method_names = ["get", "post", "patch", "delete"]
    serializer_class = ReviewSerializer
    permission_classes = (IsRedactor,)

    def get_title_id(self):
        title_id = self.kwargs.get("title_id")
        return get_object_or_404(Title, id=title_id)

    def get_queryset(self):
        return self.get_title_id().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title_id())


class CommentsViewSet(viewsets.ModelViewSet):
    """Вьюсет комментариев."""
    http_method_names = ["get", "post", "patch", "delete"]
    serializer_class = CommentsSerializer
    permission_classes = (IsRedactor,)

    def get_review_id(self):
        review_id = self.kwargs.get("review_id")
        return get_object_or_404(Review, id=review_id)

    def get_queryset(self):
        return self.get_review_id().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review_id())

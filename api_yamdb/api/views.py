"""Вьюхи приложения api."""
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import TitleFitler
from .permissions import IsAdmin, IsRedactor, Me, ReadOnly
from .serializers import (CategorySerializer, CommentsSerializer,
                          ConfirmRegistrationSerializer, GenreSerializer,
                          RegistrationSerializer, ReviewSerializer,
                          TitleGetSerializer, TitlePostSerializer,
                          UserSerializer)
from .utils import (CategoryGenreMixinSet, generate_short_hash_mm3,
                    send_email_confirm)

from reviews.models import Category, Genre, Review, Title, User  # isort: skip


class RegistrationAPIView(APIView):
    """Создает нового пользователя. Отправляет код подтверждения."""
    serializer_class = RegistrationSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        """ Создаем или обновялем пользователя с текущим временем
            в поле updated_at, которое затем используется для генерации
            кода подтверждения.
        """
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, created = serializer.save(
            defaults={'updated_at': timezone.now})

        code = generate_short_hash_mm3(
            f'{user.username}{user.email}{user.updated_at}')

        # Отправка кода на email
        send_email_confirm(user.email, code)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ConfirmationEmailAPIView(APIView):
    """Подтверждает регистрацию пользователя. Обновляет токен"""
    serializer_class = ConfirmRegistrationSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ConfirmRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('username')

        token = str(RefreshToken.for_user(user).access_token)

        return Response({'token': token}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """Позволяет выполнить все операции CRUD с пользователями."""
    http_method_names = ('get', 'post', 'patch', 'delete')
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (IsAdmin,)
    filter_backends = (SearchFilter,)
    search_fields = ('username',)


class MeRetrieveUpdateViewSet(mixins.RetrieveModelMixin,
                              mixins.UpdateModelMixin,
                              viewsets.GenericViewSet):
    http_method_names = ('get', 'patch')
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (Me,)


class GenreViewSet(CategoryGenreMixinSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (ReadOnly, IsAdmin)


class CategoryViewSet(CategoryGenreMixinSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (ReadOnly, IsAdmin)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFitler
    permission_classes = (ReadOnly, IsAdmin)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        serializer_classes = {
            'create': TitlePostSerializer,
            'update': TitlePostSerializer,
            'partial_update': TitlePostSerializer
        }
        default_serializer = TitleGetSerializer
        return serializer_classes.get(self.action, default_serializer)


class ReviewViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = ReviewSerializer
    permission_classes = (IsRedactor,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        serializer.save(author=self.request.user, title_id=title_id)


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer
    permission_classes = (IsRedactor,)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        serializer.save(author=self.request.user, review_id=review_id)

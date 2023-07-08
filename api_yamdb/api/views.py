"""Вьюхи приложения api."""
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from reviews.models import Category, Genre, Review, Title
from .filters import TitleFitler
from .serializers import (CategorySerializer, CommentsSerializer,
                          ConfirmRegistrationSerializer, GenreSerializer,
                          RegistrationSerializer, ReviewSerializer,
                          TitleGetSerializer, TitlePostSerializer)
from .utils import CategoryGenreMixinSet


class RegistrationAPIView(APIView):
    """Создает нового пользователя. Обновляет токен."""
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConfirmationEmailAPIView(APIView):
    """Подтверждает регистрацию пользователя."""
    serializer_class = ConfirmRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        # serializer.delete()

        return Response({'token': 'token'}, status=status.HTTP_200_OK)


class GenreViewSet(CategoryGenreMixinSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(CategoryGenreMixinSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFitler
    permission_classes = ()
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
    permission_classes = ()

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        serializer.save(author=self.request.user, title_id=title_id)


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer
    permission_classes = ()

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        serializer.save(author=self.request.user, review_id=review_id)

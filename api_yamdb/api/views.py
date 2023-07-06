"""Вьюхи приложения api."""
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import TitleFitler
from .serializers import (ConfirmRegistrationSerializer,
                          RegistrationSerializer, ReviewSerializer)
from reviews.models import Title


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


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    )
    filter_backends = ()
    permission_classes = ()
    filterset_class = TitleFitler
    http_method_names = ('get', 'post', 'patch', 'delete')

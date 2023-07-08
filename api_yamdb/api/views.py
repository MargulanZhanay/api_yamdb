"""Вьюхи приложения api."""
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (ConfirmRegistrationSerializer,
                          RegistrationSerializer, ReviewSerializer)
from .utils import generate_short_hash_mm3, send_email_confirm

from reviews.models import Title, EmailConfirmation, User  # isort: skip


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
    """Создает нового пользователя. Отправляет код подтверждения."""
    serializer_class = RegistrationSerializer

    def post(self, request):

        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, created = serializer.save(
            defaults={'updated_at': timezone.now})

        # Сохранение кода подтверждения в базе данных
        # code = get_random_string(10)
        # EmailConfirmation.objects.update_or_create(
        #     username=user,
        #     defaults={'confirmation_code': code})

        code = generate_short_hash_mm3(
            f'{user.username}{user.email}{user.updated_at}')

        # Отправка кода на email
        send_email_confirm(user, user.email, code)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ConfirmationEmailAPIView(APIView):
    """Подтверждает регистрацию пользователя. Обновляет токен"""
    serializer_class = ConfirmRegistrationSerializer

    def post(self, request):
        serializer = ConfirmRegistrationSerializer(data=request.data)
        # user = get_object_or_404(User, username=request.data.get('username'))
        # user = User.objects.filter(username=request.data.get('username')).exists()
        # if not serializer.is_valid():
        #     return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('username')

        token = str(RefreshToken.for_user(user).access_token)

        return Response({'token': token}, status=status.HTTP_200_OK)

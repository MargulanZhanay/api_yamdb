"""Вьюхи приложения api."""
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (ConfirmRegistrationSerializer,
                          RegistrationSerializer, ReviewSerializer)

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
        user = User.objects.filter(username=request.data.get('username'))

        # Если пользователь существует, просто отправляем код
        if user.exists():
            user = user[0]
            email = user.email
            self.send_email_confirm(user, email)
            return Response({'email': email, 'username': user.username},
                            status=status.HTTP_200_OK)

        # Создаем пользователя и отпраялем код.
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(**serializer.data)
        email = request.data.get('email')
        self.send_email_confirm(user, email)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def send_email_confirm(self, user: str, email: str) -> None:
        """Отправка кода подтверждения на email."""
        code = get_random_string(10)

        # Сохранение кода подтверждения в базе данных
        EmailConfirmation.objects.create(username=user,
                                         confirmation_code=code)

        # Отправка письма с кодом подтверждения
        subject = 'Подтверждение регистрации'
        message = f'Код для подтверждения регистрации: {code}'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


class ConfirmationEmailAPIView(APIView):
    """Подтверждает регистрацию пользователя. Обновляет токен"""
    serializer_class = ConfirmRegistrationSerializer

    def post(self, request):
        serializer = ConfirmRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(username=serializer.data.get('username'))
        # serializer.update(user.confirm.first(), serializer.validated_data)

        # token = str(RefreshToken.for_user(user).access_token)

        return Response({'token': 'token'}, status=status.HTTP_200_OK)

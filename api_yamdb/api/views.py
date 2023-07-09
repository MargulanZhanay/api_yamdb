"""Вьюхи приложения api."""
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (ConfirmRegistrationSerializer,
                          RegistrationSerializer, ReviewSerializer,
                          UserSerializer)
from .utils import generate_short_hash_mm3, send_email_confirm

from reviews.models import Title, User  # isort: skip


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

    def post(self, request):
        serializer = ConfirmRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('username')

        token = str(RefreshToken.for_user(user).access_token)

        return Response({'token': token}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """Позволяет выполнить все операции CRUD с пользователями."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

# class UserViewSet(viewsets.ViewSet):
#     """Позволяет выполнить все операции CRUD с пользователями."""
#     lookup_field = 'username'

#     def list(self, request):
#         queryset = User.objects.all()
#         serializer = UserSerializer(queryset, many=True)
#         return Response(serializer.data)

#     def create(self, request):
#         serializer = UserSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     def retrieve(self, request, username=None):
#         queryset = User.objects.all()
#         user = get_object_or_404(queryset, username=username)
#         serializer = UserSerializer(user)
#         return Response(serializer.data)

#     def partial_update(self, request, username=None):
#         queryset = User.objects.all()
#         user = get_object_or_404(queryset, username=username)
#         serializer = UserSerializer(user, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def destroy(self, request, username=None):
#         queryset = User.objects.all()
#         user = get_object_or_404(queryset, username=username)
#         user.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

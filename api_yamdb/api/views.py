"""Вьюхи приложения api."""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ConfirmRegistrationSerializer, RegistrationSerializer


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

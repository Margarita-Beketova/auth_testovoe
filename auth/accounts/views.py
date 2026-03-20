from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer

class RegisterView(APIView):
    """
    Регистрация нового пользователя.
    Endpoint: POST /api/auth/register/
    """

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                serializer.to_representation(user),
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    """
    Аутентификация пользователя и выдача JWT-токена.
    Endpoint: POST /api/auth/login/
    """

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.get_token()
            return Response({
                'token': token,
                'user': {
                    'id': serializer.validated_data['user'].id,
            'email': serializer.validated_data['user'].email,
            'username': serializer.validated_data['user'].username
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

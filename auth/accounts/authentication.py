
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.conf import settings
from .models import CustomUser

class CustomJWTTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header[7:] 

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = CustomUser.objects.get(id=payload['user_id'])
            return (user, token)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, CustomUser.DoesNotExist):
            raise AuthenticationFailed('Неверный или истёкший токен')


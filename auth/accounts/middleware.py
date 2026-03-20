import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .models import User 
from django.conf import settings


class JWTMiddleware(MiddlewareMixin):
    """
    Middleware для проверки JWT-токена в заголовке Authorization.
    Извлекает токен, проверяет подпись и срок действия, находит пользователя и присваивает его request.user.
    """

    def process_request(self, request):
        """
        Обрабатывает запрос: проверяет JWT-токен и устанавливает request.user.
        """
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            request.user = AnonymousUser()
            return None

        if not auth_header.startswith('Bearer '):
            return JsonResponse(
                {'detail': 'Invalid Authorization header format. Use "Bearer <token>"'},
                status=401
            )

        try:
        
            token = auth_header.split(' ', 1)[1]

           
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256']           
)

           
            user_id = payload.get('user_id')
            if not user_id:
                return JsonResponse(
                    {'detail': 'Token does not contain user ID'},
                    status=401
                )

           
            
            try:
                user = User.objects.get(id=user_id)
                if not user.is_active:
                    return JsonResponse(
                    {'detail': 'Account is deactivated'},
                     status=401
                    )
                request.user = user
            except User.DoesNotExist:
                return JsonResponse(
                    {'detail': 'User not found'},
                    status=401
                )

        except jwt.ExpiredSignatureError:
            return JsonResponse(
                {'detail': 'Token has expired'},
                status=401
            )
        except jwt.InvalidTokenError:
            return JsonResponse(
                {'detail': 'Invalid token'},
                status=401
            )
        except Exception as e:
            return JsonResponse(
                {'detail': f'Authentication error: {str(e)}'},
                status=401
            )


        return None

import jwt
import uuid
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class JWTHandler:
    """
    Универсальный обработчик для генерации и валидации JWT‑токенов.
    Обеспечивает единообразный формат payload для всех сериализаторов.
    """

    @staticmethod
    def _get_token_payload(user, token_type='access'):
        """
        Формирует унифицированный payload для JWT‑токена.
        """
        lifetime = getattr(
            settings,
            'JWT_ACCESS_TOKEN_LIFETIME',
            timedelta(hours=24)
        )
        exp_time = timezone.now() + lifetime
        iat_time = timezone.now()

        return {
            'user_id': user.id,
            'email': user.email,
            'exp': int(exp_time.timestamp()),  
            'iat': int(iat_time.timestamp()),
            'jti': str(uuid.uuid4()),
            'token_type': token_type
        }

    @classmethod
    def generate_token(cls, user, token_type='access'):
     
        try:
            payload = cls._get_token_payload(user, token_type)
            secret_key = getattr(settings, 'SECRET_KEY')
            algorithm = getattr(settings, 'JWT_ALGORITHM', 'HS256')

            token = jwt.encode(
                payload,
                secret_key,
                algorithm=algorithm
            )

            return token

        except Exception as e:
            logger.error(f"Ошибка генерации JWT для пользователя {user.id}: {e}")
            raise

    @classmethod
    def validate_token(cls, token):
    
        try:
            secret_key = getattr(settings, 'SECRET_KEY')
            algorithm = getattr(settings, 'JWT_ALGORITHM', 'HS256')

            payload = jwt.decode(
                token,
                secret_key,
                algorithms=[algorithm]
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
        except Exception as e:
            logger.error(f"Ошибка валидации JWT: {e}")
            raise

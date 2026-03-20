import bcrypt
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    password_confirm = serializers.CharField(write_only=True, min_length=8, required=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Некорректный формат email.")
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Пароль должен содержать минимум 8 символов.")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну цифру.")
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну букву.")
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Пароли не совпадают."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        user = User.objects.create(
            **validated_data,
            password_hash=hashed_password
        )
        return user

    def to_representation(self, instance):
        token = self._generate_jwt_token(instance)
        return {
            'id': instance.id,
            'email': instance.email,
            'username': instance.username,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'token': token
        }

    def _generate_jwt_token(self, user):
        payload = {
            'user_id': user.id,
            'email': user.email,
            'exp': timezone.now() + timedelta(hours=24),
            'iat': timezone.now()
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return token.decode('utf-8') if isinstance(token, bytes) else token


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError("Пользователь с таким email не найден.")
            
            if not user.is_active:
                raise serializers.ValidationError("Учетная запись деактивирована.")
            
            if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                raise serializers.ValidationError("Неверный пароль.")
            
            data['user'] = user
        else:
            raise serializers.ValidationError("Необходимо указать email и пароль.")
        
        return data

    def _generate_jwt_token(self, user):
        payload = {
            'user_id': user.id,
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return token.decode('utf-8') if isinstance(token, bytes) else token

    def get_token(self):
        return self._generate_jwt_token(self.validated_data['user'])
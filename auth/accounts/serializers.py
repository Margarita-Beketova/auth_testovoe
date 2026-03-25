import bcrypt
import jwt
import uuid
from datetime import timedelta
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers
from .models import CustomUser, AccessRule, Role
from .jwt_handler import JWTHandler


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
        
        if CustomUser.objects.filter(email=value).exists():
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
        
        user = CustomUser.objects.create(
            **validated_data,
            password_hash=hashed_password
        )
        return user

    def to_representation(self, instance):
        token = JWTHandler.generate_token(instance, 'access')
        return {
            'id': instance.id,
            'email': instance.email,
            'username': instance.username,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'token': token
        }

    



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError("Пользователь с таким email не найден.")
            
            if not user.is_active:
                raise serializers.ValidationError("Учетная запись деактивирована.")
            
            if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                raise serializers.ValidationError("Неверный пароль.")
            
            data['user'] = user
        else:
            raise serializers.ValidationError("Необходимо указать email и пароль.")
        
        return data

  
    def get_token(self):
        return JWTHandler.generate_token(
            self.validated_data['user'],
            'access'
        )
    


class UserUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    username = serializers.CharField(max_length=150, required=False)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'last_name']

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance



class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

class AccessRuleSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        source='role',
        write_only=True,
        help_text='ID роли'
    )

    class Meta:
        model = AccessRule
        fields = [
            'id',
            'role',
            'role_id',
            'permission_code',
            'description'
        ]
        read_only_fields = ['role']

    def validate_permission_code(self, value):
        """Валидация формата permission_code: объект.действие"""
        if '.' not in value:
            raise serializers.ValidationError(
                'Код разрешения должен содержать точку в формате: объект.действие (например: user.view)'
            )

        parts = value.split('.')
        if len(parts) != 2:
            raise serializers.ValidationError(
                'Код разрешения должен быть в формате: объект.действие'
            )

        resource, action = parts
        if not resource or not action:
            raise serializers.ValidationError(
                'Объект и действие не могут быть пустыми'
            )

        
        allowed_actions = ['view', 'edit', 'create', 'delete']
        if action not in allowed_actions:
            raise serializers.ValidationError(
                f'Действие должно быть одним из: {", ".join(allowed_actions)}'
            )

        return value

    def create(self, validated_data):
        return AccessRule.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Обновление существующего правила"""
        instance.role = validated_data.get('role', instance.role)
        instance.permission_code = validated_data.get('permission_code', instance.permission_code)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance

from django.db import models
from django.utils import timezone


class Role(models.Model):
    name = models.CharField(max_length=150, blank=False, verbose_name='Название')
    slug = models.SlugField(max_length=150, unique=True, verbose_name='Идентификатор')
    description = models.TextField(blank=True, verbose_name='Описание')
    is_system = models.BooleanField(default=False, verbose_name='Системная')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class User(models.Model):
    first_name = models.CharField(max_length=150, blank=False, null=False, verbose_name='Имя')
    last_name = models.CharField(max_length=150, blank=False, null=False, verbose_name='Фамилия')
    email = models.EmailField(unique=True, verbose_name='Email') 
    username = models.CharField(max_length=150, unique=True, verbose_name='Логин')
    
    password_hash = models.CharField(max_length=255, verbose_name='Хеш пароля')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Роль'
    )
   
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='Последний вход')

    
    def has_permission(self, permission_code):
        pass
    

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
        ]

    def __str__(self):
        return f"{self.last_name} {self.first_name}".strip()
    


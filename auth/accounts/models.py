from django.db import models


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

class AccessRule(models.Model):
    role = models.ForeignKey('Role', on_delete=models.CASCADE, related_name='access_rules', verbose_name='Роль')
    permission_code = models.CharField(max_length=100,
                                    help_text='Формат: объект.действие (например: product.view, order.edit)',
                                    verbose_name='Код разрешения'
    )
    
    description = models.TextField(blank=True, verbose_name='Описание')
    
    class Meta:
        verbose_name = 'Правило доступа'
        verbose_name_plural = 'Правила доступа'
        unique_together = ('role', 'permission_code')
        ordering = ['role', 'permission_code']
        indexes = [
            models.Index(fields=['permission_code']),
        ]

    def __str__(self):
        return f"{self.role.name} → {self.permission_code}"

    

class User(models.Model):
    first_name = models.CharField(max_length=150, blank=False, null=False, verbose_name='Имя')
    last_name = models.CharField(max_length=150, blank=False, null=False, verbose_name='Фамилия')
    email = models.EmailField(unique=True, verbose_name='Email') 
    username = models.CharField(max_length=150, unique=True, verbose_name='Логин')
    
    password_hash = models.CharField(max_length=255, verbose_name='Хеш пароля')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users', verbose_name='Роль')
   
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='Последний вход')

    
    def has_permission(self, permission_code):
        if not self.role:
            return False

        if self.role.access_rules.filter(permission_code='*').exists():
            return True
        return self.role.access_rules.filter(permission_code=permission_code).exists()
    

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
    


class BusinessElement(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    slug = models.SlugField(unique=True, max_length=100, verbose_name='Идентификатор')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    
    class Meta:
        verbose_name = 'Бизнес-элемент'
        verbose_name_plural = 'Бизнес-элементы'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name






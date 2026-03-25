from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=150, blank=False, verbose_name='Название')
    slug = models.SlugField(max_length=150, unique=True, verbose_name='Идентификатор')
    description = models.TextField(blank=True, verbose_name='Описание')
    is_system = models.BooleanField(default=False, verbose_name='Системная')
   

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

    

class CustomUser(models.Model):
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

    @property
    def is_anonymous(self):
        return False
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_admin(self):
        return self.role and self.role.slug == 'admin'

    
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



class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название категории')
    slug = models.SlugField(unique=True, max_length=100, verbose_name='URL-код')
    description = models.TextField(blank=True, verbose_name='Описание категории')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name



class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название товара')
    slug = models.SlugField(unique=True, max_length=100, verbose_name='URL-код')
    description = models.TextField(verbose_name='Описание товара')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    stock = models.PositiveIntegerField(verbose_name='Количество на складе')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Категория'
    )
    care_instructions = models.TextField(
        blank=True,
        verbose_name='Инструкции по уходу'
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']

    def __str__(self):
        return self.name



class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('confirmed', 'Подтверждён'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменён'),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Пользователь'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус заказа'
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Итоговая сумма'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлён')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.pk} от {self.user.username}'



class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена за единицу'
    )

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'





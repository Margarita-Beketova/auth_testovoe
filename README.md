# Система разграничения прав доступа

Django-приложение для управления аутентификацией и ролевой моделью доступа.

## Возможности

- 🔐 JWT-аутентификация
- 👥 Ролевая модель (Admin, Manager, User)
- 🔒 Гранулярные права доступа (`объект.действие`)
- 📦 CRUD для правил доступа

## Стек

- Django 5.2.12
- Django REST Framework 3.16.1
- PostgreSQL + psycopg2
- PyJWT + bcrypt

## Быстрый старт

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp auth/.env.example auth/.env
# Отредактируйте auth/.env (SECRET_KEY, DB_NAME, и т.д.)

# Миграции
cd auth
python manage.py migrate

# Запуск сервера
python manage.py runserver
```

## API Endpoints

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/auth/register/` | Регистрация |
| POST | `/api/auth/login/` | Вход (JWT) |
| POST | `/api/auth/logout/` | Выход |
| GET/PUT | `/api/users/me/` | Профиль |
| POST | `/api/users/me/delete/` | Удаление аккаунта |
| GET/POST | `/api/admin/rules/` | Правила доступа (admin) |
| GET/PUT/DELETE | `/api/admin/rules/{id}/` | Правило (admin) |

## Модель прав доступа

```
Роль → AccessRule → permission_code
```

**Формат:** `{объект}.{действие}`

| Действие | Код |
|----------|-----|
| Просмотр | `view` |
| Создание | `create` |
| Редактирование | `edit` |
| Удаление | `delete` |
| Полный доступ | `*` |

## Примеры использования

```http
POST /api/auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "securepassword123",
  "password_confirm": "securepassword123",
  "first_name": "Имя",
  "last_name": "Фамилия"
}
```

```http
POST /api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}

# Ответ: { "token": "eyJ...", "user": {...} }
```

## Лицензия

MIT

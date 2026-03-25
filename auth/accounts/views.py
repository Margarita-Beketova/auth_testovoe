from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer, UserUpdateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from .permissions import CustomPermission, IsAdminUser
from .serializers import AccessRuleSerializer
from .models import AccessRule



class RegisterView(APIView):
    permission_classes = []
    """
    Регистрация 
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
    permission_classes = []
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




class LogoutView(APIView):
    """
    Выход из системы.
    Endpoint: POST /api/auth/logout/

    """

    def post(self, request):
        
        return Response({
            'detail': 'Вы успешно вышли из системы.'
        }, status=status.HTTP_200_OK)




class UserProfileView(APIView):
    """
    Обновление данных пользователя.
    Endpoint: PUT /api/users/me/
    Требуется аутентификация (JWT-токен).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Получение данных текущего пользователя."""
        serializer = UserUpdateSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        """Обновление данных текущего пользователя."""
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserUpdateSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteAccountView(APIView):
    """
    Удаление аккаунта (деактивация).
    Endpoint: POST /api/users/me/delete/
        
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        user.is_active = False
        user.save()

        
        return Response({
            'detail': 'Ваш аккаунт был успешно деактивирован. Все данные сохранены, но доступ заблокирован.'
        }, status=status.HTTP_200_OK)



class AccessRuleListView(ListCreateAPIView):
    """
    API для списка правил доступа и создания новых.
    GET /api/rules/ — список всех правил
    POST /api/rules/ — создание нового правила
    Доступ только для администраторов.
    """
    queryset = AccessRule.objects.select_related('role').all()
    serializer_class = AccessRuleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def list(self, request, *args, **kwargs):
        """Переопределяем list для добавления мета‑информации"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })

class AccessRuleDetailView(RetrieveUpdateDestroyAPIView):
    """
    API для работы с конкретным правилом доступа.
    GET /api/rules/{id}/ — получение правила
    PUT /api/rules/{id}/ — полное обновление
    PATCH /api/rules/{id}/ — частичное обновление
    DELETE /api/rules/{id}/ — удаление правила
    Доступ только для администраторов.
    """
    queryset = AccessRule.objects.select_related('role').all()
    serializer_class = AccessRuleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        """Кастомное удаление с подтверждением"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'detail': f'Правило доступа "{instance}" успешно удалено.'
        }, status=status.HTTP_200_OK)



class BusinessObjectsMockView(APIView):
    """
    Mock-view для бизнес‑объектов.
    Endpoint: GET /api/business-objects/
    Проверяет аутентификацию и права через CustomPermission.
    При успешном доступе возвращает статический JSON с данными.
    """
    permission_classes = [CustomPermission]

    def get(self, request):
        """
        Возвращает статический список бизнес‑объектов (например, заказов).
        Доступ разрешён только аутентифицированным пользователям с соответствующими правами.
        """
       
        mock_data = {
            "count": 3,
            "results": [
                {
                    "id": 1,
            "order_number": "ORD-2023-001",
            "customer_name": "Иван Петров",
            "total_amount": 2500.00,
            "status": "completed",
            "created_at": "2023-10-15T10:30:00Z",
            "items": [
                {"product": "Монстера", "quantity": 1, "price": 2000.00},
                {"product": "Фиалка", "quantity": 1, "price": 500.00}
            ]
        },
        {
            "id": 2,
            "order_number": "ORD-2023-002",
            "customer_name": "Мария Сидорова",
            "total_amount": 1800.00,
            "status": "pending",
            "created_at": "2023-10-16T14:15:00Z",
            "items": [
                {"product": "Роза чайная", "quantity": 1, "price": 800.00},
                {"product": "Эхеверия", "quantity": 1, "price": 1000.00}
            ]
        },
        {
            "id": 3,
            "order_number": "ORD-2023-003",
            "customer_name": "Алексей Козлов",
            "total_amount": 4200.00,
            "status": "shipped",
            "created_at": "2023-10-17T09:45:00Z",
            "items": [
                {"product": "Седум", "quantity": 1, "price": 3500.00},
                {"product": "Эониум", "quantity": 1, "price": 700.00}
            ]
        }
            ]
        }

        return Response(mock_data, status=status.HTTP_200_OK)


from django.urls import path
from . import views

urlpatterns = [
    path('api/auth/register/', views.RegisterView.as_view(), name='auth-register'),
    path('api/auth/login/', views.LoginView.as_view(), name='auth-login'),
]

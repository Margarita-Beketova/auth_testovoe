from django.urls import path
from . import views

urlpatterns = [
    path('api/auth/register/', views.RegisterView.as_view(), name='auth-register'),
    path('api/auth/login/', views.LoginView.as_view(), name='auth-login'),
    path('api/auth/logout/', views.LogoutView.as_view(), name='auth-logout'),
    path('api/users/me/', views.UserProfileView.as_view(), name='user-profile'),
    path('api/users/me/delete/', views.DeleteAccountView.as_view(), name='delete-account'),
    path('api/rules/', views.AccessRuleListView.as_view(), name='access-rule-list'),
    path('api/rules/<int:id>/', views.AccessRuleDetailView.as_view(), name='access-rule-detail'),
    path('api/business-objects/', views.BusinessObjectsMockView.as_view(), name='business-objects'),


]

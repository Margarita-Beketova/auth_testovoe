# permissions.py
from rest_framework.permissions import BasePermission
from .models import AccessRule

class CustomPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if user is None or not getattr(user, 'is_active', False):
            return False
        
        if user.is_admin:
            return True

        permission_code = self._get_permission_code(request, view)
        if not permission_code:
            return False

        return self._has_access_via_roles(user, permission_code)

    def has_object_permission(self, request, view, obj):
        """
        Проверка доступа к конкретному объекту.
        """
        user = request.user
        
        if not user.is_authenticated or not user.is_active:
            return False
        

        permission_code = self._get_permission_code(request, view)
        
       
        if hasattr(obj, 'owner') and obj.owner == user:
            return self._has_access_via_roles(user, permission_code)
        
        
        return self._has_access_via_roles(user, permission_code)

    def _get_permission_code(self, request, view):
        resource = self._get_resource_name(view)

        
        action = self._get_action_from_method(request.method)
        if not resource or not action:
            return None

        return f"{resource}.{action}"

    def _get_resource_name(self, view):
      
        if hasattr(view, 'resource_name'):
            return view.resource_name

        class_name = view.__class__.__name__
        resource_name = class_name.lower().replace('view', '').replace('apiview', '')
        return resource_name

    def _get_action_from_method(self, method):
        method_action_map = {
            'GET': 'view',
            'PUT': 'edit',
            'PATCH': 'edit',
            'DELETE': 'delete',
            'POST': 'create',
            'OPTIONS': 'view',  
            'HEAD': 'view',   
        }
        return method_action_map.get(method)

    def _has_access_via_roles(self, user, permission_code):
        if not user.role:
            return False
        if AccessRule.objects.filter(
            role=user.role, 
            permission_code='*'
            ).exists():
            return True

        return AccessRule.objects.filter(
        role=user.role,
        permission_code=permission_code
    ).exists()

class IsAdminUser(CustomPermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


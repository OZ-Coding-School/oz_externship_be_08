from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """admin만 접근 가능"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'


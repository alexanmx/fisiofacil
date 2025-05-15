from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsProfissionalOrAdmin(permissions.BasePermission):
    """
    Permissão que permite apenas profissionais autenticados ou admin acessar.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class IsAuthenticatedAndReadOnly(permissions.BasePermission):
    """
    Permite acesso somente para usuários autenticados.
    Só permite leitura (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return False

class IsAuthenticatedAndNoDelete(permissions.BasePermission):
    """
    Permite tudo (GET, POST, PUT) para usuário autenticado,
    mas bloqueia DELETE.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method == 'DELETE':
            return False
        return True
    

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser


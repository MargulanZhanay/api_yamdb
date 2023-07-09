from rest_framework.permissions import SAFE_METHODS, BasePermission

REDACTORS = ['admin', 'moderator']


class IsRedactor(BasePermission):
    """Проверяет право пользователя на редактирвоание."""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'POST':
            return request.user.is_authenticated
        return ((obj.author == request.user or request.user.role in REDACTORS)
                and request.user.is_authenticated)


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == 'admin' or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return request.user.role == 'admin' or request.user.is_staff


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS


class Me(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj

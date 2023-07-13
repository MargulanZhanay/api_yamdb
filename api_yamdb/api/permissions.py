from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsRedactor(BasePermission):
    """Чтение - все.
    Создание - авторизованные пользователи.
    Редактирование - автор, модератор, админ."""
    def has_permission(self, request, view):
        return request.user.is_authenticated or request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.method == "POST":
            return request.user.is_authenticated
        return (
            obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderator
        ) and request.user.is_authenticated


class IsAdmin(BasePermission):
    """Права админа."""
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_admin or request.user.is_staff
        return False

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_admin
            or request.user.is_staff
        ) and request.user.is_authenticated


class ReadOnly(BasePermission):
    """Права на чтение всем, без токена."""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS


class Me(BasePermission):
    """Права на получение/изменение своего профиля,
    авторизованному пользователю."""
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj

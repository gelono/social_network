from rest_framework.permissions import BasePermission

SAFE_HTTP_METHODS = ['GET', 'HEAD']


class IsAdminOrReadOnly(BasePermission):
    """
    This class determines the depth of access to information depending on user rights
    """
    def has_permission(self, request, view):
        user = request.user

        if user.is_staff:
            return True
        if request.method in SAFE_HTTP_METHODS:
            return True

        return False


class IsAdminOrPostOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_staff:
            return True
        if obj.user == user:
            return True

        return False

# commerce/permissions.py
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Custom admin check: allow Django superusers and role='admin'.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_superuser or getattr(request.user, "role", None) == "admin")
        )


class IsSellerOrReadOnly(permissions.BasePermission):
    """
    Only sellers (or admins) can create/update/delete products.
    Everyone can read (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and (getattr(request.user, "role", None) in ["seller", "admin"] or request.user.is_superuser)
        )


class IsOwner(permissions.BasePermission):
    """
    Customers can only access their own objects.
    Admins have full access.
    """
    def has_object_permission(self, request, view, obj):
        # Allow admins
        if request.user.is_superuser or getattr(request.user, "role", None) == "admin":
            return True

        # Check ownership on user-related fields
        if hasattr(obj, "user") and obj.user == request.user:
            return True
        if hasattr(obj, "order") and hasattr(obj.order, "user") and obj.order.user == request.user:
            return True
        if hasattr(obj, "cart") and hasattr(obj.cart, "user") and obj.cart.user == request.user:
            return True

        return False

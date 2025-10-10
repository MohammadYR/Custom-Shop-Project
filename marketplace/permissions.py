from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):
    """
    خواندن برای همه آزاد؛ نوشتن فقط اگر مالک شیء باشی:
    - Seller → obj.user == request.user
    - Store → obj.owner.user == request.user
    - StoreItem → obj.store.owner.user == request.user
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        # Seller
        owner_user_id = None
        if hasattr(obj, "user"):
            owner_user_id = getattr(obj.user, "id", None)
        # Store
        elif hasattr(obj, "owner"):
            owner_user_id = getattr(getattr(obj.owner, "user", None), "id", None)
        # StoreItem
        elif hasattr(obj, "store") and hasattr(obj.store, "owner"):
            owner_user_id = getattr(getattr(obj.store.owner, "user", None), "id", None)

        return owner_user_id is not None and request.user.is_authenticated and owner_user_id == request.user.id

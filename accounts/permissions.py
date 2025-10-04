from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        Checks if the object is owned by the current user.

        :param request: The request object.
        :param view: The view object.
        :param obj: The object to check.
        :return: True if the object is owned by the current user, False otherwise.
        """
        user = getattr(obj, "user", None) or obj
        return user == request.user

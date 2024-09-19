from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class IsAdminOrThreadParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants of a thread or admin to delete/view.
    """

    def has_object_permission(self, request, view, obj):
        # Check if user is admin
        if request.user.is_superuser:
            return True
        # Check if user is a participant of the thread
        return request.user in obj.participants.all()


class IsThreadParticipant(permissions.BasePermission):
    """
    A permission class that checks if a user is a member of a thread.
    """
    def has_object_permission(self, request, view, obj):

        if request.user not in obj.participants.all():
            raise PermissionDenied("You are not a member of this thread")
        return True


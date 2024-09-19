from rest_framework import permissions

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


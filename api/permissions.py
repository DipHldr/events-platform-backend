from rest_framework import permissions

class IsFacilitator(permissions.BasePermission):
    """Allows access only to verified facilitators."""
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                hasattr(request.user, 'profile') and 
                request.user.profile.role == 'facilitator' and
                request.user.profile.is_verified)

class IsSeeker(permissions.BasePermission):
    """Allows access only to verified seekers."""
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                hasattr(request.user, 'profile') and 
                request.user.profile.role == 'seeker' and
                request.user.profile.is_verified)
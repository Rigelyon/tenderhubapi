from rest_framework import permissions

class IsProfileOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to handle profile access permissions.
    
    For user profiles:
    - GET requests are allowed for any authenticated user
    - PUT/PATCH requests are only allowed for the profile owner
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the profile owner
        return obj == request.user or obj.user == request.user

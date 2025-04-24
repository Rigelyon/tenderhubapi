from rest_framework import permissions

class IsClientOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow clients to create tenders.
    """
    def has_permission(self, request, view):
        # Allow read permissions for any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to clients
        return request.user.is_authenticated and request.user.is_client
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the client who owns the tender
        return obj.client == request.user

class IsVendorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow vendors to place bids.
    """
    def has_permission(self, request, view):
        # Allow read permissions for any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to vendors
        return request.user.is_authenticated and request.user.is_vendor
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the vendor who placed the bid
        return obj.vendor == request.user

class IsProjectParticipant(permissions.BasePermission):
    """
    Custom permission to only allow project participants to view and edit.
    """
    def has_object_permission(self, request, view, obj):
        # Permission is only allowed to client or vendor of the project
        return obj.client == request.user or obj.vendor == request.user
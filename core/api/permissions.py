from rest_framework import permissions

class IsAdminRole(permissions.BasePermission):
    """
    Custom permission to only allow users with the 'admin' role.
    This is different from Django's built-in is_staff permission.
    """
    
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False
            
        # Check if the user has the 'admin' role
        return request.user.role == 'admin'
        
class IsCompanyRole(permissions.BasePermission):
    """
    Custom permission to only allow users with the 'company' role.
    """
    
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False
            
        # Check if the user has the 'company' role
        return request.user.role == 'company'
        
class IsVolunteerRole(permissions.BasePermission):
    """
    Custom permission to only allow users with the 'volunteer' role.
    """
    
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False
            
        # Check if the user has the 'volunteer' role
        return request.user.role == 'volunteer'
        
class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admin users to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin users can edit anything
        if request.user.role == 'admin':
            return True
            
        # Check if the object has a user field and if it matches the request user
        if hasattr(obj, 'user'):
            return obj.user == request.user
            
        return False

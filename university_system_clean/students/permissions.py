from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Permission class for Admin users only.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'


class IsStaff(permissions.BasePermission):
    """
    Permission class for Staff users only.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'STAFF'


class IsTeacher(permissions.BasePermission):
    """
    Permission class for Teacher users only.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'TEACHER'


class IsStudent(permissions.BasePermission):
    """
    Permission class for Student users only.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'STUDENT'


class IsAdminOrStaff(permissions.BasePermission):
    """
    Permission class for Admin or Staff users.
    """
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                request.user.role in ['ADMIN', 'STAFF'])


class IsAdminOrTeacher(permissions.BasePermission):
    """
    Permission class for Admin or Teacher users.
    """
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                request.user.role in ['ADMIN', 'TEACHER'])


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class that allows owners to access their own data, or admin to access any.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ADMIN':
            return True
        
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        if hasattr(obj, 'student') and hasattr(request.user, 'student_profile'):
            return obj.student == request.user.student_profile
        
        return False

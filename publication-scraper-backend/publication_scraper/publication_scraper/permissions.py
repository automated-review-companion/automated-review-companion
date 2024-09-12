from rest_framework.permissions import BasePermission

class IsReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in ['GET', 'HEAD', 'OPTIONS']
      
class IsReadWrite(BasePermission):
    def has_permission(self, request, view):
        return request.method in ['POST', 'PUT', 'PATCH', 'DELETE']
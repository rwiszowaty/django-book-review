from rest_framework.permissions import BasePermission


class HasUsername(BasePermission):
    message = "Musisz ustawić nazwę użytkownika, aby dodać recenzję."

    def has_permission(self, request, view):
        return request.user.is_authenticated and bool(request.user.username)

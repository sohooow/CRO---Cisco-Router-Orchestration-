from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Interface, Log, Router, User


class RouterAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return (
            request.user.is_superuser or getattr(request.user, "role", None) == "admin"
        )

    def has_change_permission(self, request, obj=None):
        return (
            request.user.is_superuser or getattr(request.user, "role", None) == "admin"
        )

    def has_delete_permission(self, request, obj=None):
        return (
            request.user.is_superuser or getattr(request.user, "role", None) == "admin"
        )


admin.site.register(Router, RouterAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Interface)
admin.site.register(Log)

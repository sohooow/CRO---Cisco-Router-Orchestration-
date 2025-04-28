from django.contrib import admin
from .models import User, Router, Interface, Log 

# Register your models here.

class RouterAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return request.user.role == 'admin'

    def has_change_permission(self, request, obj=None):
        return request.user.role == 'admin'

    def has_delete_permission(self, request, obj=None):
        return request.user.role == 'admin'


admin.site.register(Router, RouterAdmin)
admin.site.register(User)
admin.site.register(Interface)
admin.site.register(Log)

from django.contrib import admin
from .models import User, Router, Interface, Configuration, Log 

# Register your models here.

admin.site.register(Router)
admin.site.register(User)
admin.site.register(Interface)
admin.site.register(Configuration)
admin.site.register(Log)

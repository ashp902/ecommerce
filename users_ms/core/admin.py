from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address

# Register models
admin.site.register(User)
admin.site.register(Address)
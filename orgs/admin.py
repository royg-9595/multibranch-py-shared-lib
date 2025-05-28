from django.contrib import admin
from .models import Organization, Role, CustomUser

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_main')


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'organization', 'role', 'is_org_admin')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization')
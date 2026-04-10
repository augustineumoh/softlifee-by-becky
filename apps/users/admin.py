from apps.core.admin_site import softlifee_admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address


class UserAdmin(BaseUserAdmin):
    list_display  = ['email', 'first_name', 'last_name', 'phone', 'is_staff', 'date_joined']
    list_filter   = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering      = ['-date_joined']

    fieldsets = (
        (None,            {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'avatar')}),
        ('Permissions',   {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates',         {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    readonly_fields = ['date_joined', 'last_login']


class AddressAdmin:
    list_display  = ['user', 'label', 'city', 'state', 'is_default']
    list_filter   = ['state', 'is_default']
    search_fields = ['user__email', 'full_name', 'city']


softlifee_admin.register(User, UserAdmin)
softlifee_admin.register(Address)
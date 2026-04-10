from django.contrib import admin
from django.utils import timezone
from .discount import DiscountCode, DiscountUsage


class DiscountUsageInline(admin.TabularInline):
    model         = DiscountUsage
    extra         = 0
    readonly_fields = ['user', 'order', 'used_at']
    can_delete    = False

    def has_add_permission(self, request, obj=None):
        return False


class DiscountCodeAdmin(admin.ModelAdmin):
    list_display   = ['code', 'discount_type', 'value', 'minimum_order',
                      'usage_count', 'usage_limit', 'is_active',
                      'valid_from', 'valid_until', 'is_currently_valid']
    list_filter    = ['discount_type', 'is_active', 'first_order_only']
    list_editable  = ['is_active']
    search_fields  = ['code']
    ordering       = ['-created_at']
    inlines        = [DiscountUsageInline]
    readonly_fields = ['usage_count', 'created_at']

    fieldsets = (
        ('Code',       {'fields': ('code', 'is_active')}),
        ('Discount',   {'fields': ('discount_type', 'value', 'maximum_discount', 'minimum_order')}),
        ('Validity',   {'fields': ('valid_from', 'valid_until')}),
        ('Usage',      {'fields': ('usage_limit', 'usage_count', 'per_user_limit', 'first_order_only')}),
    )

    def is_currently_valid(self, obj):
        now = timezone.now()
        valid = (
            obj.is_active and
            now >= obj.valid_from and
            (not obj.valid_until or now <= obj.valid_until) and
            (not obj.usage_limit or obj.usage_count < obj.usage_limit)
        )
        return '✅ Valid' if valid else '❌ Invalid'
    is_currently_valid.short_description = 'Status'

    actions = ['activate_codes', 'deactivate_codes']

    def activate_codes(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} code(s) activated.')
    activate_codes.short_description = 'Activate selected codes'

    def deactivate_codes(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} code(s) deactivated.')
    deactivate_codes.short_description = 'Deactivate selected codes'

# Re-register with custom admin site
from apps.core.admin_site import softlifee_admin
from .discount import DiscountCode, DiscountUsage

softlifee_admin.register(DiscountCode, DiscountCodeAdmin)
softlifee_admin.register(DiscountUsage)
from django.contrib import admin
from .models import Order, OrderItem
from apps.core.emails import send_order_status_email
from .discount_admin import *  # noqa — registers DiscountCode and DiscountUsage admins
from apps.core.admin_site import softlifee_admin


class OrderItemInline(admin.TabularInline):
    model         = OrderItem
    extra         = 0
    readonly_fields = ['product', 'product_name', 'product_price', 'quantity', 'subtotal']
    can_delete    = False

    def has_add_permission(self, request, obj=None):
        return False


class OrderAdmin(admin.ModelAdmin):
    list_display   = ['order_number', 'customer_name', 'customer_email',
                      'total', 'status', 'payment_status', 'payment_method',
                      'delivery_state', 'created_at']
    list_filter    = ['status', 'payment_status', 'payment_method',
                      'delivery_state', 'created_at']
    list_editable  = ['status']
    search_fields  = ['order_number', 'customer_email', 'customer_name',
                      'customer_phone', 'paystack_ref']
    ordering       = ['-created_at']
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            send_order_status_email(obj)
        super().save_model(request, obj, form, change)

    readonly_fields = ['order_number', 'subtotal', 'delivery_fee', 'total',
                       'paystack_ref', 'paystack_txn_id', 'paid_at',
                       'created_at', 'updated_at']
    inlines        = [OrderItemInline]

    fieldsets = (
        ('Order Info',    {'fields': ('order_number', 'status', 'created_at')}),
        ('Customer',      {'fields': ('user', 'customer_name', 'customer_email', 'customer_phone')}),
        ('Delivery',      {'fields': ('delivery_address', 'delivery_city', 'delivery_state', 'delivery_notes')}),
        ('Financials',    {'fields': ('subtotal', 'delivery_fee', 'total')}),
        ('Payment',       {'fields': ('payment_method', 'payment_status', 'paystack_ref', 'paystack_txn_id', 'paid_at')}),
    )


softlifee_admin.register(Order, OrderAdmin)
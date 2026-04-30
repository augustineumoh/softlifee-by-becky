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
        super().save_model(request, obj, form, change)
        if not change:
            return

        # Admin confirms payment → send order confirmation email
        payment_confirmed = (
            'payment_status' in form.changed_data and obj.payment_status == 'paid'
        )
        status_confirmed = (
            'status' in form.changed_data and obj.status == 'confirmed'
        )
        if payment_confirmed or status_confirmed:
            if obj.payment_status == 'paid' and not obj.paid_at:
                from django.utils import timezone
                obj.__class__.objects.filter(pk=obj.pk).update(paid_at=timezone.now())
            try:
                from apps.core.emails import send_order_confirmation_email
                send_order_confirmation_email(obj)
            except Exception:
                pass
            return

        # Other status changes → send status-specific email
        if 'status' in form.changed_data and obj.status in (
            'processing', 'shipped', 'delivered', 'cancelled'
        ):
            try:
                send_order_status_email(obj)
            except Exception:
                pass

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
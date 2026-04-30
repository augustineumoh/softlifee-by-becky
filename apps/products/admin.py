from django.contrib import admin
from django.utils.html import format_html, mark_safe
from .models import (
    Category, Subcategory, Product, ProductImage,
    ColorVariant, ProductVideo, Wishlist, StockHistory,
)
from apps.core.admin_site import softlifee_admin


class SubcategoryInline(admin.TabularInline):
    model  = Subcategory
    extra  = 1
    fields = ['name', 'slug', 'order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}


class CategoryAdmin(admin.ModelAdmin):
    list_display        = ['name', 'slug', 'is_active', 'order']
    list_editable       = ['order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    inlines             = [SubcategoryInline]


class ProductImageInline(admin.TabularInline):
    model  = ProductImage
    extra  = 1
    fields = ['image', 'alt_text', 'is_primary', 'order']


class ColorVariantInline(admin.TabularInline):
    model  = ColorVariant
    extra  = 1
    fields = ['label', 'hex_code', 'image', 'order', 'is_active']


class ProductVideoInline(admin.TabularInline):
    model  = ProductVideo
    extra  = 1
    fields = ['video_url', 'poster', 'order']


class ProductAdmin(admin.ModelAdmin):
    list_display        = ['name', 'category', 'price', 'badge', 'inventory_status',
                           'stock_count', 'rating', 'review_count', 'is_active', 'added_date']
    list_filter         = ['category', 'badge', 'in_stock', 'is_active', 'added_date']
    list_editable       = ['price', 'stock_count', 'is_active']
    search_fields       = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering            = ['-created_at']
    inlines             = [ProductImageInline, ColorVariantInline, ProductVideoInline]
    actions             = ['send_new_arrival_newsletter']

    @admin.action(description='📧 Send new arrival newsletter for selected products')
    def send_new_arrival_newsletter(self, request, queryset):
        from apps.newsletter.models import NewsletterSubscriber
        from apps.newsletter.emails import send_newsletter_blast
        from django.conf import settings

        products = list(queryset[:6])
        if not products:
            self.message_user(request, 'No products selected.', level='warning')
            return

        names = ', '.join(p.name for p in products)
        subject = f'New Arrivals at Soft Lifee 🛍️'
        heading = 'Something new just dropped ✨'

        product_lines = ''.join(
            f'<p style="margin:8px 0"><strong style="color:#8A4FB1">{p.name}</strong>'
            f' — ₦{p.price:,.0f}</p>'
            for p in products
        )
        body_html = (
            f'<p>We\'ve just added fresh new pieces to the store — '
            f'and you\'re the first to know.</p>'
            f'{product_lines}'
            f'<p style="margin-top:16px">Head over to our shop to grab yours before they sell out!</p>'
        )

        subscribers = NewsletterSubscriber.objects.filter(is_active=True)
        count = subscribers.count()
        if count == 0:
            self.message_user(request, 'No active subscribers.', level='warning')
            return

        try:
            send_newsletter_blast(
                subscribers,
                subject=subject,
                heading=heading,
                body_html=body_html,
                cta_label='Shop New Arrivals',
                cta_url=f"{settings.FRONTEND_URL}/new-arrivals",
            )
            self.message_user(request, f'New arrival newsletter sent to {count} subscriber(s) for: {names}.')
        except Exception as e:
            self.message_user(request, f'Error sending newsletter: {e}', level='error')

    fieldsets = (
        ('Basic Info',   {'fields': ('name', 'slug', 'category', 'subcategory', 'badge')}),
        ('Content',      {'fields': ('description', 'details')}),
        ('Pricing',      {'fields': ('price', 'sale_price', 'sale_start', 'sale_end')}),
        ('Inventory',    {'fields': ('in_stock', 'stock_count')}),
        ('Stats',        {'fields': ('rating', 'review_count')}),
        ('Visibility',   {'fields': ('is_active',)}),
    )
    readonly_fields = ['rating', 'review_count']

    def inventory_status(self, obj):
        # Guard against NULL stock_count (can occur in seeded data)
        stock = obj.stock_count if obj.stock_count is not None else 0
        if not obj.in_stock or stock == 0:
            return mark_safe(
                '<span style="background:#FEF2F2;color:#DC2626;padding:3px 10px;'
                'border-radius:12px;font-size:0.72rem;font-weight:600">Out of Stock</span>'
            )
        if stock <= 5:
            return format_html(
                '<span style="background:#FFFBEB;color:#D97706;padding:3px 10px;'
                'border-radius:12px;font-size:0.72rem;font-weight:600">Low Stock ({})</span>',
                stock,
            )
        return format_html(
            '<span style="background:#F0FDF4;color:#16A34A;padding:3px 10px;'
            'border-radius:12px;font-size:0.72rem;font-weight:600">In Stock ({})</span>',
            stock,
        )
    inventory_status.short_description = 'Inventory'

    def save_model(self, request, obj, form, change):
        old_stock = None
        if change and 'stock_count' in form.changed_data:
            try:
                old_stock = Product.objects.get(pk=obj.pk).stock_count or 0
            except Product.DoesNotExist:
                pass

        super().save_model(request, obj, form, change)

        # Log stock change
        if old_stock is not None:
            new_stock       = obj.stock_count or 0
            quantity_change = new_stock - old_stock
            if quantity_change != 0:
                try:
                    StockHistory.objects.create(
                        product         = obj,
                        action          = 'added' if quantity_change > 0 else 'removed',
                        quantity_change = quantity_change,
                        stock_before    = old_stock,
                        stock_after     = new_stock,
                        created_by      = request.user,
                    )
                except Exception:
                    pass

        # Low-stock alert (obj.in_stock was synced by model's save())
        stock = obj.stock_count or 0
        if 0 < stock <= 5:
            try:
                from apps.core.emails import send_low_stock_alert
                send_low_stock_alert(obj)
            except Exception:
                pass


class StockHistoryAdmin(admin.ModelAdmin):
    list_display    = ['product', 'action_badge', 'qty_change', 'stock_before',
                       'stock_after', 'note', 'created_by', 'created_at']
    list_filter     = ['action', 'created_at']
    search_fields   = ['product__name', 'note', 'created_by__email']
    ordering        = ['-created_at']
    readonly_fields = ['product', 'action', 'quantity_change', 'stock_before',
                       'stock_after', 'created_by', 'created_at']

    def has_add_permission(self, _request):
        return False  # history is auto-logged, not manually created

    def action_badge(self, obj):
        colors = {
            'added':      ('#F0FDF4', '#16A34A'),
            'removed':    ('#FEF2F2', '#DC2626'),
            'adjustment': ('#FFFBEB', '#D97706'),
            'sale':       ('#EFF6FF', '#2563EB'),
            'return':     ('#F5F3FF', '#7C3AED'),
        }
        bg, fg = colors.get(obj.action, ('#F3F4F6', '#6B7280'))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;'
            'border-radius:12px;font-size:0.72rem;font-weight:600">{}</span>',
            bg, fg, obj.get_action_display(),
        )
    action_badge.short_description = 'Action'

    def qty_change(self, obj):
        color = '#16A34A' if obj.quantity_change > 0 else '#DC2626'
        sign  = '+' if obj.quantity_change > 0 else ''
        return format_html(
            '<strong style="color:{}">{}{}</strong>',
            color, sign, obj.quantity_change,
        )
    qty_change.short_description = 'Change'


class WishlistAdmin(admin.ModelAdmin):
    list_display  = ['user', 'product', 'created_at']
    list_filter   = ['created_at']
    search_fields = ['user__email', 'product__name']


softlifee_admin.register(Category,     CategoryAdmin)
softlifee_admin.register(Product,      ProductAdmin)
softlifee_admin.register(StockHistory, StockHistoryAdmin)
softlifee_admin.register(Wishlist,     WishlistAdmin)

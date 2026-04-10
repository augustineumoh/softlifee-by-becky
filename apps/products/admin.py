from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Subcategory, Product, ProductImage,
    ColorVariant, ProductVideo, Wishlist
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
    list_display        = ['name', 'category', 'price', 'badge', 'in_stock',
                           'stock_count', 'rating', 'review_count', 'is_active', 'added_date']
    list_filter         = ['category', 'badge', 'in_stock', 'is_active', 'added_date']
    list_editable       = ['price', 'in_stock', 'stock_count', 'is_active']
    search_fields       = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering            = ['-created_at']
    inlines             = [ProductImageInline, ColorVariantInline, ProductVideoInline]

    fieldsets = (
        ('Basic Info',   {'fields': ('name', 'slug', 'category', 'subcategory', 'badge')}),
        ('Content',      {'fields': ('description', 'details')}),
        ('Pricing',      {'fields': ('price', 'in_stock', 'stock_count')}),
        ('Stats',        {'fields': ('rating', 'review_count')}),
        ('Visibility',   {'fields': ('is_active',)}),
    )
    readonly_fields = ['rating', 'review_count']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Send low stock alert when stock drops to 5 or below
        if obj.stock_count <= 5 and obj.in_stock:
            try:
                from apps.core.emails import send_low_stock_alert
                send_low_stock_alert(obj)
            except Exception:
                pass


class WishlistAdmin(admin.ModelAdmin):
    list_display  = ['user', 'product', 'created_at']
    list_filter   = ['created_at']
    search_fields = ['user__email', 'product__name']


softlifee_admin.register(Category, CategoryAdmin)
softlifee_admin.register(Product, ProductAdmin)
softlifee_admin.register(Wishlist, WishlistAdmin)
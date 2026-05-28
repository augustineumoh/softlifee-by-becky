from rest_framework import serializers
from django.conf import settings
from .models import (
    Category, Subcategory, Product, ProductImage,
    ColorVariant, ProductVideo, Wishlist, RecentlyViewed, SizeVariant
)


def _cloudinary_url(raw: str) -> str:
    """Convert a Cloudinary stored path to a full https:// URL.

    cloudinary_storage saves paths as 'image/upload/{public_id}' (with or
    without a version prefix).  We strip the 'image/upload/' segment and
    re-build a delivery URL with sensible defaults so the frontend never
    needs to know the cloud name.
    """
    if not raw:
        return ''
    if raw.startswith('http'):
        return raw
    cloud = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', '')
    if not cloud:
        return raw
    public_id = raw.removeprefix('image/upload/')
    return f'https://res.cloudinary.com/{cloud}/image/upload/q_auto,f_auto/{public_id}'


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Subcategory
        fields = ['id', 'name', 'slug']


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True)
    image         = serializers.SerializerMethodField()

    class Meta:
        model  = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'subcategories']

    def get_image(self, obj):
        return _cloudinary_url(str(obj.image)) if obj.image else None


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model  = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']

    def get_image(self, obj):
        return _cloudinary_url(str(obj.image)) if obj.image else None


class ColorVariantSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model  = ColorVariant
        fields = ['id', 'label', 'hex_code', 'image', 'in_stock', 'stock_count', 'order']

    def get_image(self, obj):
        return _cloudinary_url(str(obj.image)) if obj.image else None


class ProductVideoSerializer(serializers.ModelSerializer):
    poster = serializers.SerializerMethodField()

    class Meta:
        model  = ProductVideo
        fields = ['id', 'video_url', 'poster', 'order']

    def get_poster(self, obj):
        return _cloudinary_url(str(obj.poster)) if obj.poster else None


class SizeVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SizeVariant
        fields = ['id', 'label', 'size_type', 'in_stock', 'stock_count', 'order']


# ── Product list (lightweight) ────────────────────────────────────────────────
class ProductListSerializer(serializers.ModelSerializer):
    category         = serializers.StringRelatedField()
    subcategory      = serializers.StringRelatedField()
    primary_image    = serializers.SerializerMethodField()
    badge_display    = serializers.CharField(source='get_badge_display', read_only=True)
    is_new           = serializers.ReadOnlyField()
    is_on_sale       = serializers.ReadOnlyField()
    active_price     = serializers.ReadOnlyField()
    discount_percent = serializers.ReadOnlyField()
    sale_end         = serializers.DateTimeField(read_only=True)

    class Meta:
        model  = Product
        fields = [
            'id', 'name', 'slug', 'category', 'subcategory',
            'price', 'sale_price', 'active_price', 'is_on_sale',
            'discount_percent', 'sale_end',
            'badge', 'badge_display', 'primary_image',
            'rating', 'review_count', 'in_stock', 'stock_count', 'is_new', 'added_date',
        ]

    def get_primary_image(self, obj):
        img = obj.images.filter(is_primary=True).first() or obj.images.first()
        if img:
            return ProductImageSerializer(img, context=self.context).data
        return None


# ── Product detail (full) ─────────────────────────────────────────────────────
class ProductDetailSerializer(serializers.ModelSerializer):
    category         = CategorySerializer(read_only=True)
    subcategory      = SubcategorySerializer(read_only=True)
    images           = ProductImageSerializer(many=True, read_only=True)
    color_variants   = ColorVariantSerializer(many=True, read_only=True)
    size_variants    = SizeVariantSerializer(many=True, read_only=True)
    videos           = ProductVideoSerializer(many=True, read_only=True)
    badge_display    = serializers.CharField(source='get_badge_display', read_only=True)
    is_new           = serializers.ReadOnlyField()
    is_on_sale       = serializers.ReadOnlyField()
    active_price     = serializers.ReadOnlyField()
    discount_percent = serializers.ReadOnlyField()
    is_wishlisted    = serializers.SerializerMethodField()

    class Meta:
        model  = Product
        fields = [
            'id', 'name', 'slug', 'category', 'subcategory',
            'description', 'details', 'price', 'sale_price', 'sale_start', 'sale_end',
            'active_price', 'is_on_sale', 'discount_percent',
            'badge', 'badge_display',
            'images', 'color_variants', 'size_variants', 'videos',
            'rating', 'review_count', 'in_stock', 'stock_count',
            'is_new', 'is_wishlisted', 'added_date',
        ]

    def get_is_wishlisted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Wishlist.objects.filter(user=request.user, product=obj).exists()
        return False


# ── Wishlist ──────────────────────────────────────────────────────────────────
class WishlistSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model  = Wishlist
        fields = ['id', 'product', 'created_at']


# ── Recently Viewed ───────────────────────────────────────────────────────────
class RecentlyViewedSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model  = RecentlyViewed
        fields = ['id', 'product', 'viewed_at']
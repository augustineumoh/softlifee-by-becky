from rest_framework import serializers
from django.utils.text import slugify
from .models import Category, Subcategory, Product, ProductImage, ColorVariant, SizeVariant, ProductVideo


class ProductCreateSerializer(serializers.Serializer):
    """Accepts JSON to create a new product. Images are uploaded separately."""
    name         = serializers.CharField(max_length=255)
    slug         = serializers.SlugField(max_length=255, required=False, allow_blank=True)
    category     = serializers.SlugRelatedField(queryset=Category.objects.all(), slug_field='slug')
    subcategory  = serializers.SlugRelatedField(queryset=Subcategory.objects.all(), slug_field='slug', required=False, allow_null=True)
    description  = serializers.CharField()
    details      = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    price        = serializers.DecimalField(max_digits=12, decimal_places=2)
    sale_price   = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    sale_start   = serializers.DateTimeField(required=False, allow_null=True)
    sale_end     = serializers.DateTimeField(required=False, allow_null=True)
    badge        = serializers.ChoiceField(choices=['new', 'best_seller', 'top_rated', 'trending', 'premium', ''], required=False, default='')
    in_stock     = serializers.BooleanField(required=False, default=True)
    stock_count  = serializers.IntegerField(min_value=0, required=False, default=0)

    def validate_slug(self, value):
        if value and Product.objects.filter(slug=value).exists():
            raise serializers.ValidationError('A product with this slug already exists.')
        return value

    def validate(self, attrs):
        if not attrs.get('slug'):
            base = slugify(attrs['name'])
            slug = base
            n = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f'{base}-{n}'
                n += 1
            attrs['slug'] = slug
        return attrs

    def create(self, validated_data):
        return Product.objects.create(**validated_data)


class ProductUpdateSerializer(serializers.Serializer):
    """All fields optional — only supplied fields are updated."""
    name        = serializers.CharField(max_length=255, required=False)
    category    = serializers.SlugRelatedField(queryset=Category.objects.all(), slug_field='slug', required=False)
    subcategory = serializers.SlugRelatedField(queryset=Subcategory.objects.all(), slug_field='slug', required=False, allow_null=True)
    description = serializers.CharField(required=False)
    details     = serializers.ListField(child=serializers.CharField(), required=False)
    price       = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    sale_price  = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    sale_start  = serializers.DateTimeField(required=False, allow_null=True)
    sale_end    = serializers.DateTimeField(required=False, allow_null=True)
    badge       = serializers.ChoiceField(choices=['new', 'best_seller', 'top_rated', 'trending', 'premium', ''], required=False)
    in_stock    = serializers.BooleanField(required=False)
    stock_count = serializers.IntegerField(min_value=0, required=False)
    is_active   = serializers.BooleanField(required=False)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ImageUploadSerializer(serializers.Serializer):
    image      = serializers.ImageField()
    alt_text   = serializers.CharField(max_length=200, required=False, allow_blank=True)
    is_primary = serializers.BooleanField(required=False, default=False)
    order      = serializers.IntegerField(min_value=0, required=False, default=0)


class ColorVariantSerializer(serializers.Serializer):
    label    = serializers.CharField(max_length=50)
    hex_code = serializers.CharField(max_length=7)
    image    = serializers.ImageField()
    order    = serializers.IntegerField(min_value=0, required=False, default=0)


class ColorVariantUpdateSerializer(serializers.Serializer):
    label    = serializers.CharField(max_length=50, required=False)
    hex_code = serializers.CharField(max_length=7, required=False)
    image    = serializers.ImageField(required=False)
    order    = serializers.IntegerField(min_value=0, required=False)


class SizeVariantSerializer(serializers.Serializer):
    label       = serializers.CharField(max_length=20)
    size_type   = serializers.ChoiceField(choices=['clothing', 'shoes', 'numeric'], required=False, default='clothing')
    in_stock    = serializers.BooleanField(required=False, default=True)
    stock_count = serializers.IntegerField(min_value=0, required=False, default=0)
    order       = serializers.IntegerField(min_value=0, required=False, default=0)


class SizeVariantUpdateSerializer(serializers.Serializer):
    label       = serializers.CharField(max_length=20, required=False)
    in_stock    = serializers.BooleanField(required=False)
    stock_count = serializers.IntegerField(min_value=0, required=False)
    order       = serializers.IntegerField(min_value=0, required=False)


class VideoAddSerializer(serializers.Serializer):
    video_url = serializers.URLField()
    order     = serializers.IntegerField(min_value=0, required=False, default=0)

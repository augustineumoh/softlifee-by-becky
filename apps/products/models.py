from django.db import models
from django.utils import timezone
from cloudinary.models import CloudinaryField


class Category(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image       = CloudinaryField('image', blank=True, null=True)
    order       = models.PositiveIntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    category    = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name        = models.CharField(max_length=100)
    slug        = models.SlugField()
    description = models.TextField(blank=True)
    order       = models.PositiveIntegerField(default=0)
    is_active   = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Subcategories'
        unique_together = ['category', 'slug']
        ordering = ['order', 'name']

    def __str__(self):
        return f'{self.category.name} → {self.name}'


class Product(models.Model):
    BADGE_CHOICES = [
        ('new',         'New'),
        ('best_seller', 'Best Seller'),
        ('top_rated',   'Top Rated'),
        ('trending',    'Trending'),
        ('premium',     'Premium'),
    ]

    name         = models.CharField(max_length=255)
    slug         = models.SlugField(unique=True)
    category     = models.ForeignKey(Category,    on_delete=models.PROTECT, related_name='products')
    subcategory  = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    description  = models.TextField()
    details      = models.JSONField(default=list, blank=True)   # list of bullet points
    price        = models.DecimalField(max_digits=12, decimal_places=2)
    sale_price   = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    sale_start   = models.DateTimeField(null=True, blank=True)
    sale_end     = models.DateTimeField(null=True, blank=True)
    badge        = models.CharField(max_length=20, choices=BADGE_CHOICES, blank=True)
    is_active    = models.BooleanField(default=True)
    in_stock     = models.BooleanField(default=True)
    stock_count  = models.PositiveIntegerField(default=0)
    rating       = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    review_count = models.PositiveIntegerField(default=0)
    added_date   = models.DateField(auto_now_add=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def is_new(self):
        from datetime import date, timedelta
        return (date.today() - self.added_date).days <= 21

    @property
    def is_on_sale(self):
        if not self.sale_price:
            return False
        now = timezone.now()
        if self.sale_start and now < self.sale_start:
            return False
        if self.sale_end and now > self.sale_end:
            return False
        return True

    @property
    def active_price(self):
        return self.sale_price if self.is_on_sale else self.price

    @property
    def discount_percent(self):
        if self.is_on_sale and self.sale_price and self.price > 0:
            return round(((self.price - self.sale_price) / self.price) * 100)
        return 0

    def update_rating(self):
        from apps.reviews.models import Review
        reviews = Review.objects.filter(product=self, is_approved=True)
        if reviews.exists():
            self.rating       = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.review_count = reviews.count()
            self.save(update_fields=['rating', 'review_count'])


class ProductImage(models.Model):
    product   = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image     = CloudinaryField('image')
    alt_text  = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order     = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-is_primary', 'order']

    def __str__(self):
        return f'{self.product.name} — image {self.order}'

    def save(self, *args, **kwargs):
        # Only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class ColorVariant(models.Model):
    product     = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='color_variants')
    label       = models.CharField(max_length=50)   # e.g. "Desert Sage"
    hex_code    = models.CharField(max_length=7)    # e.g. "#8FAF8F"
    image       = CloudinaryField('image')
    is_active   = models.BooleanField(default=True)
    order       = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.product.name} — {self.label}'


class ProductVideo(models.Model):
    product     = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='videos')
    video_url   = models.URLField()                             # Cloudinary or YouTube URL
    poster      = CloudinaryField('poster', blank=True, null=True)
    order       = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.product.name} — video {self.order}'


class Wishlist(models.Model):
    user       = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='wishlist')
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} → {self.product.name}'


class RecentlyViewed(models.Model):
    user       = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='recently_viewed')
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='viewed_by')
    viewed_at  = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-viewed_at']

    def __str__(self):
        return f'{self.user.email} → {self.product.name}'


class SizeVariant(models.Model):
    SIZE_TYPE_CHOICES = [
        ('clothing', 'Clothing'),
        ('shoes',    'Shoes'),
        ('numeric',  'Numeric'),
    ]

    product     = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='size_variants')
    label       = models.CharField(max_length=20)      # XS, S, M, L, XL or UK6, UK7, etc.
    size_type   = models.CharField(max_length=20, choices=SIZE_TYPE_CHOICES, default='clothing')
    stock_count = models.PositiveIntegerField(default=0)
    in_stock    = models.BooleanField(default=True)
    order       = models.PositiveIntegerField(default=0)

    class Meta:
        ordering        = ['order', 'label']
        unique_together = ['product', 'label']

    def __str__(self):
        return f'{self.product.name} — Size {self.label}'


class StockHistory(models.Model):
    ACTION_CHOICES = [
        ('added',      'Stock Added'),
        ('removed',    'Stock Removed'),
        ('adjustment', 'Manual Adjustment'),
        ('sale',       'Sale Deduction'),
        ('return',     'Return / Refund'),
    ]

    product         = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_history')
    action          = models.CharField(max_length=20, choices=ACTION_CHOICES)
    quantity_change = models.IntegerField()           # positive = added, negative = removed
    stock_before    = models.PositiveIntegerField()
    stock_after     = models.PositiveIntegerField()
    note            = models.TextField(blank=True)
    created_by      = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering         = ['-created_at']
        verbose_name     = 'Stock History'
        verbose_name_plural = 'Stock History'

    def __str__(self):
        sign = '+' if self.quantity_change >= 0 else ''
        return f'{self.product.name} — {self.get_action_display()} ({sign}{self.quantity_change})'
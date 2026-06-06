from django.db import models
from django.conf import settings
from django.utils import timezone


class Cart(models.Model):
    user       = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Cart — {self.user.email}'

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.select_related('product').all())

    @property
    def item_count(self):
        return self.items.count()


class CartItem(models.Model):
    cart          = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product       = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity      = models.PositiveIntegerField(default=1)
    color_variant = models.CharField(max_length=100, blank=True)
    size_variant  = models.CharField(max_length=100, blank=True)
    added_at      = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['cart', 'product', 'color_variant', 'size_variant']
        ordering        = ['-added_at']

    def __str__(self):
        return f'{self.product.name} × {self.quantity}'

    @property
    def subtotal(self):
        return self.product.active_price * self.quantity


class CartSession(models.Model):
    """
    One row per shopping window per user.
    Opens when the user adds their first item (or first item after converting).
    Stays open until they place an order (converted=True) or go idle for 24h (abandoned).
    """
    user          = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_sessions'
    )
    started_at    = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(default=timezone.now, db_index=True)
    converted     = models.BooleanField(default=False, db_index=True)
    order         = models.ForeignKey(
        'orders.Order', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='cart_sessions'
    )
    converted_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        state = 'converted' if self.converted else 'open'
        return f'CartSession({self.user.email}, {state}, {self.started_at:%Y-%m-%d})'

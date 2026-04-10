from django.db import models
from django.utils import timezone
from decimal import Decimal


class DiscountCode(models.Model):
    TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed',      'Fixed Amount'),
    ]

    code             = models.CharField(max_length=50, unique=True, db_index=True)
    discount_type    = models.CharField(max_length=20, choices=TYPE_CHOICES, default='percentage')
    value            = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    maximum_discount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    valid_from       = models.DateTimeField(default=timezone.now)
    valid_until      = models.DateTimeField(null=True, blank=True)
    usage_limit      = models.PositiveIntegerField(null=True, blank=True)
    usage_count      = models.PositiveIntegerField(default=0)
    per_user_limit   = models.PositiveIntegerField(default=1)
    is_active        = models.BooleanField(default=True)
    first_order_only = models.BooleanField(default=False)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.code} — {self.get_discount_type_display()} {self.value}'

    def is_valid(self, user=None, subtotal=0):
        now = timezone.now()
        if not self.is_active:
            return False, 'This discount code is inactive.'
        if self.valid_until and now > self.valid_until:
            return False, 'This discount code has expired.'
        if now < self.valid_from:
            return False, 'This discount code is not yet active.'
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False, 'This discount code has reached its usage limit.'
        if subtotal < self.minimum_order:
            return False, f'Minimum order of {self.minimum_order:,.0f} required.'
        if user and user.is_authenticated:
            user_usage = DiscountUsage.objects.filter(code=self, user=user).count()
            if user_usage >= self.per_user_limit:
                return False, 'You have already used this discount code.'
            if self.first_order_only:
                from apps.orders.models import Order
                if Order.objects.filter(user=user, payment_status='paid').exists():
                    return False, 'This code is only valid on your first order.'
        return True, 'Valid'

    def calculate_discount(self, subtotal):
        if self.discount_type == 'percentage':
            discount = subtotal * (self.value / Decimal('100'))
            if self.maximum_discount:
                discount = min(discount, self.maximum_discount)
        else:
            discount = min(self.value, subtotal)
        return round(discount, 2)

    def apply(self, user=None, order=None):
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
        if user and user.is_authenticated:
            DiscountUsage.objects.create(code=self, user=user, order=order)


class DiscountUsage(models.Model):
    code    = models.ForeignKey(DiscountCode, on_delete=models.CASCADE, related_name='usages')
    user    = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='discount_usages')
    order   = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True)
    used_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email} used {self.code.code}'
from django.db import models
from django.conf import settings


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',    'Pending'),
        ('confirmed',  'Confirmed'),
        ('processing', 'Processing'),
        ('shipped',    'Shipped'),
        ('delivered',  'Delivered'),
        ('cancelled',  'Cancelled'),
        ('refunded',   'Refunded'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('card',     'Card Payment'),
        ('transfer', 'Bank Transfer'),
        ('ussd',     'USSD'),
        ('pod',      'Pay on Delivery'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('paid',     'Paid'),
        ('failed',   'Failed'),
        ('refunded', 'Refunded'),
    ]

    # Customer
    user            = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='orders'
    )
    # Allow guest checkout — store customer info directly
    customer_name   = models.CharField(max_length=200)
    customer_email  = models.EmailField()
    customer_phone  = models.CharField(max_length=20)

    # Delivery address
    delivery_address = models.TextField()
    delivery_city    = models.CharField(max_length=100)
    delivery_state   = models.CharField(max_length=100)
    delivery_notes   = models.TextField(blank=True)

    # Financials
    subtotal        = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_fee    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total           = models.DecimalField(max_digits=12, decimal_places=2)

    # Order status
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Payment
    payment_method  = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='card')
    payment_status  = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    paystack_ref    = models.CharField(max_length=200, blank=True, unique=True, null=True)
    paystack_txn_id = models.CharField(max_length=200, blank=True)
    paid_at         = models.DateTimeField(null=True, blank=True)

    # Order number (human readable)
    order_number    = models.CharField(max_length=20, unique=True, blank=True)

    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order_number} — {self.customer_email}'

    def save(self, *args, **kwargs):
        if not self.order_number:
            import random, string
            self.order_number = 'SL-' + ''.join(
                random.choices(string.digits, k=8)
            )
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order       = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product     = models.ForeignKey(
        'products.Product', on_delete=models.SET_NULL,
        null=True, related_name='order_items'
    )
    product_name  = models.CharField(max_length=255)   # snapshot at time of order
    product_price = models.DecimalField(max_digits=12, decimal_places=2)
    product_image = models.URLField(blank=True)
    color_variant = models.CharField(max_length=100, blank=True)
    quantity      = models.PositiveIntegerField(default=1)
    subtotal      = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.product_name} × {self.quantity}'

    def save(self, *args, **kwargs):
        self.subtotal = self.product_price * self.quantity
        super().save(*args, **kwargs)
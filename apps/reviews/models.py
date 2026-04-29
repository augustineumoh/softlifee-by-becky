from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    product    = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE, related_name='reviews'
    )
    user       = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviews'
    )
    # Store name even for guest reviews
    reviewer_name  = models.CharField(max_length=100)
    reviewer_email = models.EmailField(blank=True)
    city           = models.CharField(max_length=100, blank=True, default='')

    rating     = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title      = models.CharField(max_length=200, blank=True)
    body       = models.TextField()

    is_approved       = models.BooleanField(default=False)
    is_verified_purchase = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reviewer_name} — {self.product.name} ({self.rating}★)'

    def save(self, *args, **kwargs):
        # Pull name/email from user if logged in
        if self.user and not self.reviewer_name:
            self.reviewer_name  = self.user.full_name or self.user.email
            self.reviewer_email = self.user.email

        # Check if verified purchase
        if self.user and not self.is_verified_purchase:
            from apps.orders.models import Order
            self.is_verified_purchase = Order.objects.filter(
                user=self.user,
                items__product=self.product,
                payment_status='paid'
            ).exists()

        super().save(*args, **kwargs)

        # Update product rating after save
        self.product.update_rating()
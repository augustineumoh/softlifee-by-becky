from django.contrib import admin
from .models import Review


class ReviewAdmin(admin.ModelAdmin):
    list_display   = ['reviewer_name', 'product', 'rating', 'is_approved',
                      'is_verified_purchase', 'created_at']
    list_filter    = ['is_approved', 'is_verified_purchase', 'rating', 'created_at']
    list_editable  = ['is_approved']
    search_fields  = ['reviewer_name', 'reviewer_email', 'product__name', 'body']
    ordering       = ['-created_at']
    readonly_fields = ['is_verified_purchase', 'created_at', 'updated_at']

    fieldsets = (
        ('Review',   {'fields': ('product', 'user', 'reviewer_name', 'reviewer_email')}),
        ('Content',  {'fields': ('rating', 'title', 'body')}),
        ('Status',   {'fields': ('is_approved', 'is_verified_purchase')}),
        ('Dates',    {'fields': ('created_at', 'updated_at')}),
    )

    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        # Update ratings for affected products
        for review in queryset:
            review.product.update_rating()
        self.message_user(request, f'{queryset.count()} review(s) approved.')
    approve_reviews.short_description = 'Approve selected reviews'

    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        for review in queryset:
            review.product.update_rating()
        self.message_user(request, f'{queryset.count()} review(s) rejected.')
    reject_reviews.short_description = 'Reject selected reviews'

# Re-register with custom admin site
from apps.core.admin_site import softlifee_admin
from .models import Review
softlifee_admin.register(Review, ReviewAdmin)
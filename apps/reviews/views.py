from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.products.models import Product
from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer


class ProductReviewListView(generics.ListAPIView):
    """List all approved reviews for a product."""
    serializer_class   = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        slug = self.kwargs['slug']
        return Review.objects.filter(
            product__slug=slug,
            is_approved=True
        ).order_by('-created_at')


class CreateReviewView(generics.CreateAPIView):
    """Submit a review for a product."""
    serializer_class   = ReviewCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        slug    = self.kwargs['slug']
        product = get_object_or_404(Product, slug=slug, is_active=True)

        # Prevent duplicate reviews from same user
        if request.user.is_authenticated:
            if Review.objects.filter(product=product, user=request.user).exists():
                return Response(
                    {'error': 'You have already reviewed this product.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review = serializer.save(
            product = product,
            user    = request.user if request.user.is_authenticated else None,
            # Auto-approve if verified purchase, else pending
            is_approved = False,
        )

        return Response({
            'message': 'Thank you for your review! It will appear once approved.',
            'review':  ReviewSerializer(review).data,
        }, status=status.HTTP_201_CREATED)


class MyReviewsView(generics.ListAPIView):
    """List all reviews submitted by the logged-in user."""
    serializer_class   = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).order_by('-created_at')
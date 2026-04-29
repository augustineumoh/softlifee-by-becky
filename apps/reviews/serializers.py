from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    is_verified_purchase = serializers.ReadOnlyField()

    class Meta:
        model  = Review
        fields = [
            'id', 'reviewer_name', 'city', 'rating', 'title', 'body',
            'is_verified_purchase', 'created_at',
        ]
        read_only_fields = ['id', 'is_verified_purchase', 'created_at']


class FeaturedReviewSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model  = Review
        fields = ['id', 'reviewer_name', 'city', 'rating', 'body', 'product_name', 'created_at']


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Review
        fields = ['rating', 'title', 'body', 'reviewer_name', 'reviewer_email', 'city']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value

    def validate(self, data):
        # If not authenticated, reviewer_name is required
        request = self.context.get('request')
        if not request.user.is_authenticated and not data.get('reviewer_name'):
            raise serializers.ValidationError({'reviewer_name': 'Name is required.'})
        return data
from rest_framework import generics, status, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import (
    Category, Product, Wishlist, RecentlyViewed
)
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    WishlistSerializer, RecentlyViewedSerializer
)


# ── Categories ────────────────────────────────────────────────────────────────
class CategoryListView(generics.ListAPIView):
    queryset           = Category.objects.filter(is_active=True).prefetch_related('subcategories')
    serializer_class   = CategorySerializer
    permission_classes = [permissions.AllowAny]


# ── Products list with filtering ──────────────────────────────────────────────
class ProductListView(generics.ListAPIView):
    serializer_class   = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class   = None   # return all products; frontend handles display pagination
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['name', 'description', 'category__name', 'subcategory__name']
    ordering_fields    = ['price', 'created_at', 'rating', 'name']
    ordering           = ['-created_at']

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related(
            'category', 'subcategory'
        ).prefetch_related('images')

        # Filter by category slug
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category__slug=category)

        # Filter by subcategory slug
        subcategory = self.request.query_params.get('subcategory')
        if subcategory:
            qs = qs.filter(subcategory__slug=subcategory)

        # Filter by badge
        badge = self.request.query_params.get('badge')
        if badge:
            qs = qs.filter(badge=badge)

        # Filter new arrivals (added within 21 days)
        new_arrivals = self.request.query_params.get('new_arrivals')
        if new_arrivals == 'true':
            from datetime import date, timedelta
            cutoff = date.today() - timedelta(days=21)
            qs = qs.filter(badge='new', added_date__gte=cutoff)

        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)

        # Filter in stock only
        in_stock = self.request.query_params.get('in_stock')
        if in_stock == 'true':
            qs = qs.filter(in_stock=True)

        # Filter on-sale products
        on_sale = self.request.query_params.get('on_sale')
        if on_sale == 'true':
            from django.utils import timezone
            now = timezone.now()
            qs = qs.filter(
                sale_price__isnull=False
            ).filter(
                Q(sale_start__isnull=True) | Q(sale_start__lte=now)
            ).filter(
                Q(sale_end__isnull=True) | Q(sale_end__gte=now)
            )

        return qs


# ── Product detail ────────────────────────────────────────────────────────────
class ProductDetailView(generics.RetrieveAPIView):
    serializer_class   = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field       = 'slug'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related(
            'category', 'subcategory'
        ).prefetch_related('images', 'color_variants', 'size_variants', 'videos')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Track recently viewed for authenticated users
        if request.user.is_authenticated:
            RecentlyViewed.objects.update_or_create(
                user=request.user, product=instance
            )
            # Keep only last 20 viewed products per user
            viewed_ids = RecentlyViewed.objects.filter(
                user=request.user
            ).order_by('-viewed_at').values_list('id', flat=True)[20:]
            RecentlyViewed.objects.filter(id__in=list(viewed_ids)).delete()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# ── Related products ──────────────────────────────────────────────────────────
class RelatedProductsView(generics.ListAPIView):
    serializer_class   = ProductListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        slug    = self.kwargs['slug']
        product = get_object_or_404(Product, slug=slug, is_active=True)
        return Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(slug=slug).prefetch_related('images')[:8]


# ── Wishlist ──────────────────────────────────────────────────────────────────
class WishlistView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        items = Wishlist.objects.filter(user=request.user).select_related(
            'product__category'
        ).prefetch_related('product__images')
        serializer = WishlistSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        """Toggle wishlist — add if not there, remove if already there."""
        slug    = request.data.get('slug')
        product = get_object_or_404(Product, slug=slug, is_active=True)
        item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

        if not created:
            item.delete()
            return Response({'wishlisted': False, 'message': 'Removed from wishlist.'})

        return Response({
            'wishlisted': True,
            'message':    'Added to wishlist.',
        }, status=status.HTTP_201_CREATED)


# ── Recently Viewed ───────────────────────────────────────────────────────────
class RecentlyViewedView(generics.ListAPIView):
    serializer_class   = RecentlyViewedSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RecentlyViewed.objects.filter(
            user=self.request.user
        ).select_related('product__category').prefetch_related('product__images')[:20]


class SearchAutocompleteView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if len(query) < 2:
            return Response({'results': []})

        products = Product.objects.filter(is_active=True).filter(
            Q(name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(subcategory__name__icontains=query)
        ).select_related('category').prefetch_related('images')[:8]

        results = []
        for p in products:
            img = p.images.filter(is_primary=True).first() or p.images.first()
            results.append({
                'id':       p.id,
                'name':     p.name,
                'slug':     p.slug,
                'price':    str(p.price),
                'category': p.category.name,
                'image':    img.image.url if img else None,
                'type':     'product',
            })

        categories = Category.objects.filter(name__icontains=query, is_active=True)[:3]
        for cat in categories:
            results.append({'name': cat.name, 'slug': cat.slug, 'type': 'category'})

        return Response({'results': results, 'query': query})
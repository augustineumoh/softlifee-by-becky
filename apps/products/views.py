from rest_framework import generics, status, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import csv
import io
from django.http import HttpResponse
from django.conf import settings

from .models import (
    Category, Product, Wishlist, RecentlyViewed
)
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    WishlistSerializer, RecentlyViewedSerializer
)
from .serializers import _cloudinary_url


# ── Facebook Product Catalog Feed ─────────────────────────────────────────────
class FacebookCatalogFeedView(APIView):
    """
    Returns all active products as a CSV feed Facebook can fetch on a schedule.
    Supported format: CSV (Facebook also accepts TSV and RSS/ATOM XML).

    Feed URL: /api/v1/products/facebook-catalog/
    """
    permission_classes = [permissions.AllowAny]

    def get(self, _):
        frontend_url = getattr(settings, 'FRONTEND_URL', 'https://softlifee.com').rstrip('/')

        products = (
            Product.objects
            .filter(is_active=True)
            .select_related('category')
            .prefetch_related('images', 'color_variants')
        )

        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow([
            'id', 'title', 'description', 'availability', 'condition',
            'price', 'link', 'image_link', 'brand', 'google_product_category',
        ])

        for product in products:
            primary = next(
                (img for img in product.images.all() if img.is_primary),
                product.images.first(),
            )
            image_url = _cloudinary_url(str(primary.image)) if primary else ''
            price     = f'{float(product.active_price):.2f} NGN'
            link      = f'{frontend_url}/product/{product.slug}'
            desc      = product.description[:5000].replace('\r\n', ' ').replace('\n', ' ')

            color_variants = list(product.color_variants.all())

            if color_variants:
                for variant in color_variants:
                    variant_image = _cloudinary_url(str(variant.image)) if variant.image else image_url
                    writer.writerow([
                        f'{product.id}-{variant.id}',
                        f'{product.name} - {variant.label}',
                        desc,
                        'in stock' if variant.in_stock else 'out of stock',
                        'new',
                        price,
                        link,
                        variant_image or image_url,
                        'Soft Lifee by Becky',
                        product.category.name,
                    ])
            else:
                writer.writerow([
                    str(product.id),
                    product.name,
                    desc,
                    'in stock' if product.in_stock else 'out of stock',
                    'new',
                    price,
                    link,
                    image_url,
                    'Soft Lifee by Becky',
                    product.category.name,
                ])

        response = HttpResponse(buf.getvalue(), content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'inline; filename="facebook_catalog.csv"'
        return response


# ── Categories ────────────────────────────────────────────────────────────────
@method_decorator(cache_page(60 * 10), name='dispatch')   # 10-minute cache
class CategoryListView(generics.ListAPIView):
    queryset           = Category.objects.filter(is_active=True).prefetch_related('subcategories')
    serializer_class   = CategorySerializer
    permission_classes = [permissions.AllowAny]


# ── Products list with filtering ──────────────────────────────────────────────
@method_decorator(cache_page(60 * 2), name='dispatch')    # 2-minute cache; URL+query string = unique key per filter combo
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


# ── Related products / Recommendations ───────────────────────────────────────
class RelatedProductsView(generics.ListAPIView):
    serializer_class   = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class   = None  # always return a plain list, never paginated

    def get_queryset(self):
        slug    = self.kwargs['slug']
        product = get_object_or_404(Product, slug=slug, is_active=True)
        base_qs = Product.objects.filter(is_active=True).exclude(slug=slug).prefetch_related('images')

        # Prefer subcategory matches
        if product.subcategory:
            qs = base_qs.filter(subcategory=product.subcategory).order_by('-rating', '-review_count')
            if qs.count() >= 4:
                return qs[:8]

        # Same category
        qs = base_qs.filter(category=product.category).order_by('-rating', '-review_count')
        if qs.count() >= 4:
            return qs[:8]

        # Fallback: any active products ordered by rating
        return base_qs.order_by('-rating', '-review_count')[:8]


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


@method_decorator(cache_page(60 * 5), name='dispatch')    # 5-minute cache per query
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
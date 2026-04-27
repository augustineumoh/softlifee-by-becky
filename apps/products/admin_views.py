import cloudinary.uploader
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Product, ProductImage, ColorVariant, SizeVariant, ProductVideo
from .serializers import ProductDetailSerializer, ProductListSerializer
from .admin_serializers import (
    ProductCreateSerializer, ProductUpdateSerializer,
    ImageUploadSerializer, ColorVariantSerializer, ColorVariantUpdateSerializer,
    SizeVariantSerializer, SizeVariantUpdateSerializer, VideoAddSerializer,
)


class IsStaffOrSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and
                    (request.user.is_staff or request.user.is_superuser))


# ── Product CRUD ──────────────────────────────────────────────────────────────

class AdminProductCreateView(APIView):
    """
    POST /api/v1/products/admin/
    Create a product (JSON body). Upload images/variants via the endpoints below.
    """
    permission_classes = [IsStaffOrSuperuser]

    def post(self, request):
        serializer = ProductCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        product = serializer.save()
        return Response(
            ProductDetailSerializer(product, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class AdminProductUpdateView(APIView):
    """
    PATCH /api/v1/products/admin/<slug>/
    Update any subset of product fields.

    DELETE /api/v1/products/admin/<slug>/
    Soft-delete (is_active=False) or hard-delete with ?hard=true.
    """
    permission_classes = [IsStaffOrSuperuser]

    def get_object(self, slug):
        return get_object_or_404(Product, slug=slug)

    def patch(self, request, slug):
        product    = self.get_object(slug)
        serializer = ProductUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        product = serializer.update(product, serializer.validated_data)
        return Response(ProductDetailSerializer(product, context={'request': request}).data)

    def delete(self, request, slug):
        product = self.get_object(slug)
        if request.query_params.get('hard') == 'true':
            product.delete()
            return Response({'message': f'Product "{slug}" permanently deleted.'}, status=status.HTTP_200_OK)
        product.is_active = False
        product.save(update_fields=['is_active'])
        return Response({'message': f'Product "{slug}" deactivated.'}, status=status.HTTP_200_OK)


# ── Image management ──────────────────────────────────────────────────────────

class AdminImageUploadView(APIView):
    """
    POST /api/v1/products/admin/<slug>/images/
    Upload an image for a product (multipart/form-data).

    Fields:
        image      — the image file (required)
        alt_text   — description (optional)
        is_primary — true/false (optional, default false)
        order      — sort order (optional)
    """
    permission_classes = [IsStaffOrSuperuser]

    def post(self, request, slug):
        product    = get_object_or_404(Product, slug=slug)
        serializer = ImageUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file       = serializer.validated_data['image']
        is_primary = serializer.validated_data.get('is_primary', False)

        result = cloudinary.uploader.upload(
            file,
            folder='softlifee/products',
            resource_type='image',
        )

        image = ProductImage.objects.create(
            product    = product,
            image      = result['public_id'],
            alt_text   = serializer.validated_data.get('alt_text', product.name),
            is_primary = is_primary,
            order      = serializer.validated_data.get('order', 0),
        )

        return Response({
            'id':         image.id,
            'image':      result['secure_url'],
            'public_id':  result['public_id'],
            'alt_text':   image.alt_text,
            'is_primary': image.is_primary,
            'order':      image.order,
        }, status=status.HTTP_201_CREATED)


class AdminImageDeleteView(APIView):
    """
    DELETE /api/v1/products/admin/images/<id>/
    Remove a product image (also deletes from Cloudinary).

    PATCH /api/v1/products/admin/images/<id>/
    Set as primary image.
    """
    permission_classes = [IsStaffOrSuperuser]

    def get_object(self, pk):
        return get_object_or_404(ProductImage, pk=pk)

    def patch(self, request, pk):
        image = self.get_object(pk)
        # Clear other primary flags for this product
        ProductImage.objects.filter(product=image.product, is_primary=True).update(is_primary=False)
        image.is_primary = True
        image.save(update_fields=['is_primary'])
        return Response({'message': 'Primary image updated.'})

    def delete(self, request, pk):
        image = self.get_object(pk)
        try:
            public_id = str(image.image)
            if public_id and not public_id.startswith('http'):
                cloudinary.uploader.destroy(public_id)
        except Exception:
            pass
        image.delete()
        return Response({'message': 'Image deleted.'}, status=status.HTTP_200_OK)


# ── Color variant management ──────────────────────────────────────────────────

class AdminColorVariantView(APIView):
    """
    POST /api/v1/products/admin/<slug>/colors/
    Add a colour variant with its image (multipart/form-data).

    Fields:
        label    — e.g. "Desert Sage"
        hex_code — e.g. "#8FAF8F"
        image    — the colour swatch image file
        order    — sort order (optional)
    """
    permission_classes = [IsStaffOrSuperuser]

    def post(self, request, slug):
        product    = get_object_or_404(Product, slug=slug)
        serializer = ColorVariantSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if ColorVariant.objects.filter(product=product, label=serializer.validated_data['label']).exists():
            return Response(
                {'error': f'Colour variant "{serializer.validated_data["label"]}" already exists.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file   = serializer.validated_data['image']
        result = cloudinary.uploader.upload(file, folder='softlifee/products/colors', resource_type='image')

        variant = ColorVariant.objects.create(
            product  = product,
            label    = serializer.validated_data['label'],
            hex_code = serializer.validated_data['hex_code'],
            image    = result['public_id'],
            order    = serializer.validated_data.get('order', 0),
        )

        return Response({
            'id':       variant.id,
            'label':    variant.label,
            'hex_code': variant.hex_code,
            'image':    result['secure_url'],
            'order':    variant.order,
        }, status=status.HTTP_201_CREATED)


class AdminColorVariantDetailView(APIView):
    """
    PATCH /api/v1/products/admin/colors/<id>/
    Update label, hex_code, image, or order.

    DELETE /api/v1/products/admin/colors/<id>/
    Remove a colour variant.
    """
    permission_classes = [IsStaffOrSuperuser]

    def get_object(self, pk):
        return get_object_or_404(ColorVariant, pk=pk)

    def patch(self, request, pk):
        variant    = self.get_object(pk)
        serializer = ColorVariantUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        if 'label' in data:
            variant.label = data['label']
        if 'hex_code' in data:
            variant.hex_code = data['hex_code']
        if 'order' in data:
            variant.order = data['order']
        if 'image' in data:
            result = cloudinary.uploader.upload(data['image'], folder='softlifee/products/colors', resource_type='image')
            variant.image = result['public_id']

        variant.save()
        return Response({'id': variant.id, 'label': variant.label, 'hex_code': variant.hex_code, 'order': variant.order})

    def delete(self, request, pk):
        variant = self.get_object(pk)
        try:
            public_id = str(variant.image)
            if public_id and not public_id.startswith('http') and public_id != 'placeholder':
                cloudinary.uploader.destroy(public_id)
        except Exception:
            pass
        variant.delete()
        return Response({'message': 'Colour variant deleted.'}, status=status.HTTP_200_OK)


# ── Size variant management ───────────────────────────────────────────────────

class AdminSizeVariantView(APIView):
    """
    POST /api/v1/products/admin/<slug>/sizes/
    Add a size variant.

    Body (JSON):
        label       — e.g. "M", "UK8"
        size_type   — "clothing" | "shoes" | "numeric"
        in_stock    — true/false
        stock_count — integer
        order       — sort order
    """
    permission_classes = [IsStaffOrSuperuser]

    def post(self, request, slug):
        product    = get_object_or_404(Product, slug=slug)
        serializer = SizeVariantSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        d = serializer.validated_data

        if SizeVariant.objects.filter(product=product, label=d['label']).exists():
            return Response(
                {'error': f'Size variant "{d["label"]}" already exists.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        variant = SizeVariant.objects.create(product=product, **d)
        return Response({
            'id':          variant.id,
            'label':       variant.label,
            'size_type':   variant.size_type,
            'in_stock':    variant.in_stock,
            'stock_count': variant.stock_count,
            'order':       variant.order,
        }, status=status.HTTP_201_CREATED)


class AdminSizeVariantDetailView(APIView):
    """
    PATCH /api/v1/products/admin/sizes/<id>/   — update in_stock / stock_count / label / order
    DELETE /api/v1/products/admin/sizes/<id>/  — remove size variant
    """
    permission_classes = [IsStaffOrSuperuser]

    def get_object(self, pk):
        return get_object_or_404(SizeVariant, pk=pk)

    def patch(self, request, pk):
        variant    = self.get_object(pk)
        serializer = SizeVariantUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        for attr, value in serializer.validated_data.items():
            setattr(variant, attr, value)
        variant.save()
        return Response({
            'id':          variant.id,
            'label':       variant.label,
            'size_type':   variant.size_type,
            'in_stock':    variant.in_stock,
            'stock_count': variant.stock_count,
            'order':       variant.order,
        })

    def delete(self, request, pk):
        self.get_object(pk).delete()
        return Response({'message': 'Size variant deleted.'}, status=status.HTTP_200_OK)


# ── Video management ──────────────────────────────────────────────────────────

class AdminVideoView(APIView):
    """
    POST /api/v1/products/admin/<slug>/videos/
    Add a video URL to a product.

    Body (JSON):
        video_url — Cloudinary or YouTube/external URL
        order     — sort order (optional)
    """
    permission_classes = [IsStaffOrSuperuser]

    def post(self, request, slug):
        product    = get_object_or_404(Product, slug=slug)
        serializer = VideoAddSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        video = ProductVideo.objects.create(
            product   = product,
            video_url = serializer.validated_data['video_url'],
            order     = serializer.validated_data.get('order', 0),
        )
        return Response({'id': video.id, 'video_url': video.video_url, 'order': video.order},
                        status=status.HTTP_201_CREATED)


class AdminVideoDeleteView(APIView):
    """DELETE /api/v1/products/admin/videos/<id>/"""
    permission_classes = [IsStaffOrSuperuser]

    def delete(self, request, pk):
        video = get_object_or_404(ProductVideo, pk=pk)
        video.delete()
        return Response({'message': 'Video removed.'}, status=status.HTTP_200_OK)


# ── Admin product list ────────────────────────────────────────────────────────

class AdminProductListView(APIView):
    """
    GET /api/v1/products/admin/
    List ALL products (including inactive) for admin review.
    Supports ?is_active=false to show only deactivated.
    """
    permission_classes = [IsStaffOrSuperuser]

    def get(self, request):
        qs = Product.objects.all().select_related('category', 'subcategory').prefetch_related('images')
        is_active = request.query_params.get('is_active')
        if is_active == 'false':
            qs = qs.filter(is_active=False)
        elif is_active == 'true':
            qs = qs.filter(is_active=True)
        serializer = ProductListSerializer(qs, many=True, context={'request': request})
        return Response({'count': qs.count(), 'results': serializer.data})

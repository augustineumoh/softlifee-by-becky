from django.urls import path
from . import views, admin_views

urlpatterns = [
    # ── Public ────────────────────────────────────────────────────────────────
    path('categories/',          views.CategoryListView.as_view(),       name='category-list'),
    path('search/',              views.SearchAutocompleteView.as_view(),  name='search-autocomplete'),
    path('wishlist/',            views.WishlistView.as_view(),            name='wishlist'),
    path('recently-viewed/',     views.RecentlyViewedView.as_view(),      name='recently-viewed'),
    path('',                     views.ProductListView.as_view(),         name='product-list'),
    path('<slug:slug>/',         views.ProductDetailView.as_view(),       name='product-detail'),
    path('<slug:slug>/related/', views.RelatedProductsView.as_view(),     name='product-related'),

    # ── Admin — product CRUD ──────────────────────────────────────────────────
    path('admin/',               admin_views.AdminProductListView.as_view(),   name='admin-product-list'),
    path('admin/create/',        admin_views.AdminProductCreateView.as_view(), name='admin-product-create'),
    path('admin/<slug:slug>/',   admin_views.AdminProductUpdateView.as_view(), name='admin-product-update'),

    # ── Admin — images ────────────────────────────────────────────────────────
    path('admin/<slug:slug>/images/',  admin_views.AdminImageUploadView.as_view(),  name='admin-image-upload'),
    path('admin/images/<int:pk>/',     admin_views.AdminImageDeleteView.as_view(),  name='admin-image-detail'),

    # ── Admin — colour variants ───────────────────────────────────────────────
    path('admin/<slug:slug>/colors/', admin_views.AdminColorVariantView.as_view(),       name='admin-color-add'),
    path('admin/colors/<int:pk>/',    admin_views.AdminColorVariantDetailView.as_view(), name='admin-color-detail'),

    # ── Admin — size variants ─────────────────────────────────────────────────
    path('admin/<slug:slug>/sizes/', admin_views.AdminSizeVariantView.as_view(),       name='admin-size-add'),
    path('admin/sizes/<int:pk>/',    admin_views.AdminSizeVariantDetailView.as_view(), name='admin-size-detail'),

    # ── Admin — videos ────────────────────────────────────────────────────────
    path('admin/<slug:slug>/videos/', admin_views.AdminVideoView.as_view(),       name='admin-video-add'),
    path('admin/videos/<int:pk>/',    admin_views.AdminVideoDeleteView.as_view(), name='admin-video-delete'),
]
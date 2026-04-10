from django.urls import path
from . import views

urlpatterns = [
    path('categories/',           views.CategoryListView.as_view(),      name='category-list'),
    path('search/',               views.SearchAutocompleteView.as_view(), name='search-autocomplete'),
    path('wishlist/',             views.WishlistView.as_view(),           name='wishlist'),
    path('recently-viewed/',      views.RecentlyViewedView.as_view(),     name='recently-viewed'),
    path('',                      views.ProductListView.as_view(),        name='product-list'),
    path('<slug:slug>/',          views.ProductDetailView.as_view(),      name='product-detail'),
    path('<slug:slug>/related/',  views.RelatedProductsView.as_view(),    name='product-related'),
]
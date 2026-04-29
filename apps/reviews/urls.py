from django.urls import path
from . import views

urlpatterns = [
    path('featured/',           views.FeaturedReviewsView.as_view(),   name='featured-reviews'),
    path('my-reviews/',         views.MyReviewsView.as_view(),         name='my-reviews'),
    path('<slug:slug>/',        views.ProductReviewListView.as_view(), name='product-reviews'),
    path('<slug:slug>/submit/', views.CreateReviewView.as_view(),      name='submit-review'),
]
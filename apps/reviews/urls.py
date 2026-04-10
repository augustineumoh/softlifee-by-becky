from django.urls import path
from . import views

urlpatterns = [
    path('<slug:slug>/',        views.ProductReviewListView.as_view(), name='product-reviews'),
    path('<slug:slug>/submit/', views.CreateReviewView.as_view(),      name='submit-review'),
    path('my-reviews/',         views.MyReviewsView.as_view(),         name='my-reviews'),
]
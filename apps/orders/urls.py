from django.urls import path
from . import views
from .discount_views import ValidateDiscountCodeView
from .analytics import (
    SalesSummaryView, RevenueChartView, TopProductsView,
    OrderStatusBreakdownView, LowStockView, RecentOrdersView
)

urlpatterns = [
    # Orders
    path('',                        views.CreateOrderView.as_view(),       name='order-create'),
    path('my-orders/',              views.OrderListView.as_view(),         name='order-list'),
    path('my-orders/<int:pk>/',     views.OrderDetailView.as_view(),       name='order-detail'),

    # Paystack
    path('webhook/paystack/',       views.PaystackWebhookView.as_view(),   name='paystack-webhook'),
    path('verify/<str:reference>/', views.VerifyPaymentView.as_view(),     name='verify-payment'),

    # Discount codes
    path('discount/validate/',      ValidateDiscountCodeView.as_view(),    name='discount-validate'),

    # Analytics (admin only)
    path('analytics/summary/',      SalesSummaryView.as_view(),            name='analytics-summary'),
    path('analytics/revenue/',      RevenueChartView.as_view(),            name='analytics-revenue'),
    path('analytics/top-products/', TopProductsView.as_view(),             name='analytics-top-products'),
    path('analytics/order-status/', OrderStatusBreakdownView.as_view(),    name='analytics-order-status'),
    path('analytics/low-stock/',    LowStockView.as_view(),                name='analytics-low-stock'),
    path('analytics/recent-orders/',RecentOrdersView.as_view(),            name='analytics-recent-orders'),
]
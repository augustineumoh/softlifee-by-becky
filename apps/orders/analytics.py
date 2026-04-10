from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncDay, TruncMonth, TruncWeek
from django.utils import timezone
from datetime import timedelta

from .models import Order, OrderItem
from apps.products.models import Product
from apps.users.models import User


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class SalesSummaryView(APIView):
    """Overall sales stats — total revenue, orders, customers."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        paid_orders = Order.objects.filter(payment_status='paid')
        today       = timezone.now().date()
        month_start = today.replace(day=1)
        week_start  = today - timedelta(days=today.weekday())

        def stats(qs):
            return qs.aggregate(
                revenue     = Sum('total'),
                order_count = Count('id'),
            )

        today_qs = paid_orders.filter(created_at__date=today)
        week_qs  = paid_orders.filter(created_at__date__gte=week_start)
        month_qs = paid_orders.filter(created_at__date__gte=month_start)
        all_qs   = paid_orders

        return Response({
            'today':     {**stats(today_qs),  'date': str(today)},
            'this_week': {**stats(week_qs),   'from': str(week_start)},
            'this_month':{**stats(month_qs),  'from': str(month_start)},
            'all_time':  {**stats(all_qs),    'total_customers': User.objects.count()},
        })


class RevenueChartView(APIView):
    """Daily revenue chart for the last N days."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        days   = int(request.query_params.get('days', 30))
        since  = timezone.now() - timedelta(days=days)
        period = request.query_params.get('period', 'daily')  # daily | weekly | monthly

        trunc_fn = {
            'daily':   TruncDay,
            'weekly':  TruncWeek,
            'monthly': TruncMonth,
        }.get(period, TruncDay)

        data = (
            Order.objects
            .filter(payment_status='paid', created_at__gte=since)
            .annotate(period=trunc_fn('created_at'))
            .values('period')
            .annotate(revenue=Sum('total'), orders=Count('id'))
            .order_by('period')
        )

        return Response([
            {
                'date':    entry['period'].strftime('%Y-%m-%d'),
                'revenue': float(entry['revenue'] or 0),
                'orders':  entry['orders'],
            }
            for entry in data
        ])


class TopProductsView(APIView):
    """Best selling products by revenue and quantity."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        data  = (
            OrderItem.objects
            .filter(order__payment_status='paid')
            .values('product_id', 'product_name')
            .annotate(
                total_sold    = Sum('quantity'),
                total_revenue = Sum('subtotal'),
            )
            .order_by('-total_revenue')[:limit]
        )
        return Response(list(data))


class OrderStatusBreakdownView(APIView):
    """Count of orders by status."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = (
            Order.objects
            .values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        )
        return Response(list(data))


class LowStockView(APIView):
    """Products with stock <= 5."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        threshold = int(request.query_params.get('threshold', 5))
        products  = Product.objects.filter(
            stock_count__lte=threshold, is_active=True
        ).values('id', 'name', 'slug', 'stock_count', 'in_stock')
        return Response(list(products))


class RecentOrdersView(APIView):
    """Latest 10 orders for the dashboard."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        from .serializers import OrderSerializer
        orders = Order.objects.prefetch_related('items').order_by('-created_at')[:10]
        from .serializers import OrderSerializer
        return Response(OrderSerializer(orders, many=True).data)
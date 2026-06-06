from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum, Count, Avg, Q, F
from django.db.models.functions import TruncDay, TruncMonth, TruncWeek
from django.utils import timezone
from datetime import timedelta

from .models import Order, OrderItem
from apps.products.models import Product
from apps.users.models import User
from apps.cart.models import Cart
from apps.newsletter.models import NewsletterSubscriber


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
            agg = qs.aggregate(revenue=Sum('total'), order_count=Count('id'))
            revenue = float(agg['revenue'] or 0)
            count   = agg['order_count'] or 0
            agg['aov'] = round(revenue / count, 2) if count else 0
            agg['revenue'] = revenue
            return agg

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


class CartAbandonmentView(APIView):
    """Cart abandonment rate: carts with items vs paid orders."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        carts_with_items = Cart.objects.filter(items__isnull=False).distinct().count()
        paid_orders      = Order.objects.filter(payment_status='paid').count()

        if carts_with_items > 0:
            abandonment_rate = round(
                max(0, carts_with_items - paid_orders) / carts_with_items * 100, 2
            )
        else:
            abandonment_rate = 0

        return Response({
            'carts_with_items':   carts_with_items,
            'completed_orders':   paid_orders,
            'abandonment_rate':   abandonment_rate,
        })


class CustomerRetentionView(APIView):
    """Return customer rate: buyers with more than one paid order."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        paid_orders = Order.objects.filter(payment_status='paid', user__isnull=False)

        buyers = (
            paid_orders
            .values('user')
            .annotate(order_count=Count('id'))
        )
        total_buyers     = buyers.count()
        returning_buyers = buyers.filter(order_count__gt=1).count()
        new_buyers       = total_buyers - returning_buyers

        return Response({
            'total_buyers':       total_buyers,
            'returning_buyers':   returning_buyers,
            'new_buyers':         new_buyers,
            'retention_rate':     round(returning_buyers / total_buyers * 100, 2) if total_buyers else 0,
        })


class NewsletterStatsView(APIView):
    """Newsletter subscriber metrics."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        days  = int(request.query_params.get('days', 30))
        since = timezone.now() - timedelta(days=days)

        total       = NewsletterSubscriber.objects.count()
        active      = NewsletterSubscriber.objects.filter(is_active=True).count()
        unsubscribed = total - active

        growth = (
            NewsletterSubscriber.objects
            .filter(subscribed_at__gte=since)
            .annotate(day=TruncDay('subscribed_at'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )

        return Response({
            'total':        total,
            'active':       active,
            'unsubscribed': unsubscribed,
            'unsubscribe_rate': round(unsubscribed / total * 100, 2) if total else 0,
            'growth':       [
                {'date': entry['day'].strftime('%Y-%m-%d'), 'new_subscribers': entry['count']}
                for entry in growth
            ],
        })


class PaymentMethodBreakdownView(APIView):
    """Revenue and order count split by payment method."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = (
            Order.objects
            .filter(payment_status='paid')
            .values('payment_method')
            .annotate(order_count=Count('id'), revenue=Sum('total'))
            .order_by('-revenue')
        )
        return Response([
            {
                'payment_method': entry['payment_method'],
                'order_count':    entry['order_count'],
                'revenue':        float(entry['revenue'] or 0),
            }
            for entry in data
        ])


class GeographicBreakdownView(APIView):
    """Order count and revenue broken down by delivery state."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = (
            Order.objects
            .filter(payment_status='paid')
            .values('delivery_state')
            .annotate(order_count=Count('id'), revenue=Sum('total'))
            .order_by('-order_count')
        )
        return Response([
            {
                'state':       entry['delivery_state'],
                'order_count': entry['order_count'],
                'revenue':     float(entry['revenue'] or 0),
            }
            for entry in data
        ])


class CustomerGrowthView(APIView):
    """New user registrations over time."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        days   = int(request.query_params.get('days', 30))
        period = request.query_params.get('period', 'daily')
        since  = timezone.now() - timedelta(days=days)

        trunc_fn = {
            'daily':   TruncDay,
            'weekly':  TruncWeek,
            'monthly': TruncMonth,
        }.get(period, TruncDay)

        data = (
            User.objects
            .filter(date_joined__gte=since)
            .annotate(period=trunc_fn('date_joined'))
            .values('period')
            .annotate(new_users=Count('id'))
            .order_by('period')
        )

        total_users = User.objects.count()

        return Response({
            'total_users': total_users,
            'growth': [
                {
                    'date':      entry['period'].strftime('%Y-%m-%d'),
                    'new_users': entry['new_users'],
                }
                for entry in data
            ],
        })
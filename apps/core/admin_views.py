from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDay
from datetime import timedelta
import json


@method_decorator(staff_member_required, name='dispatch')
class AdminDashboardView(View):

    def get(self, request):
        now         = timezone.now()
        today       = now.date()
        month_start = today.replace(day=1)
        week_start  = today - timedelta(days=6)

        from apps.orders.models import Order
        from apps.products.models import Product
        from apps.users.models import User
        from apps.reviews.models import Review

        paid = Order.objects.filter(payment_status='paid')

        # ── Key metrics ───────────────────────────────────────────────────────
        total_revenue   = paid.aggregate(r=Sum('total'))['r'] or 0
        today_revenue   = paid.filter(created_at__date=today).aggregate(r=Sum('total'))['r'] or 0
        month_revenue   = paid.filter(created_at__date__gte=month_start).aggregate(r=Sum('total'))['r'] or 0
        total_orders    = Order.objects.count()
        today_orders    = Order.objects.filter(created_at__date=today).count()
        pending_orders  = Order.objects.filter(status='pending').count()
        total_customers = User.objects.filter(is_staff=False).count()
        total_products  = Product.objects.filter(is_active=True).count()
        low_stock       = Product.objects.filter(stock_count__lte=5, is_active=True).count()
        pending_reviews = Review.objects.filter(is_approved=False).count()

        # ── Revenue chart — last 14 days ──────────────────────────────────────
        chart_data = (
            paid.filter(created_at__date__gte=week_start)
            .annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(revenue=Sum('total'), orders=Count('id'))
            .order_by('day')
        )
        chart_labels  = []
        chart_revenue = []
        chart_orders  = []
        for entry in chart_data:
            chart_labels.append(entry['day'].strftime('%d %b'))
            chart_revenue.append(float(entry['revenue'] or 0))
            chart_orders.append(entry['orders'])

        # ── Order status breakdown ────────────────────────────────────────────
        status_data = (
            Order.objects.values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        )
        status_labels = [s['status'].title() for s in status_data]
        status_counts = [s['count'] for s in status_data]
        status_colors = {
            'Pending':    '#D4AF37',
            'Confirmed':  '#8A4FB1',
            'Processing': '#5B21B6',
            'Shipped':    '#3B82F6',
            'Delivered':  '#16A34A',
            'Cancelled':  '#BE123C',
            'Refunded':   '#6B7280',
        }
        donut_colors = [status_colors.get(s, '#8A4FB1') for s in status_labels]

        # ── Recent orders ─────────────────────────────────────────────────────
        recent_orders = Order.objects.order_by('-created_at')[:8]

        # ── Top products ──────────────────────────────────────────────────────
        from apps.orders.models import OrderItem
        top_products = (
            OrderItem.objects
            .filter(order__payment_status='paid')
            .values('product_name')
            .annotate(total_sold=Sum('quantity'), revenue=Sum('subtotal'))
            .order_by('-revenue')[:6]
        )

        # ── Low stock products ────────────────────────────────────────────────
        low_stock_products = Product.objects.filter(
            stock_count__lte=5, is_active=True
        ).order_by('stock_count')[:6]

        context = {
            # Metrics
            'total_revenue':   f'₦{total_revenue:,.0f}',
            'today_revenue':   f'₦{today_revenue:,.0f}',
            'month_revenue':   f'₦{month_revenue:,.0f}',
            'total_orders':    total_orders,
            'today_orders':    today_orders,
            'pending_orders':  pending_orders,
            'total_customers': total_customers,
            'total_products':  total_products,
            'low_stock':       low_stock,
            'pending_reviews': pending_reviews,

            # Charts (JSON for Chart.js)
            'chart_labels':   json.dumps(chart_labels),
            'chart_revenue':  json.dumps(chart_revenue),
            'chart_orders':   json.dumps(chart_orders),
            'status_labels':  json.dumps(status_labels),
            'status_counts':  json.dumps(status_counts),
            'donut_colors':   json.dumps(donut_colors),

            # Tables
            'recent_orders':      recent_orders,
            'top_products':       top_products,
            'low_stock_products': low_stock_products,

            # Admin context
            'title': 'Dashboard',
            'has_permission': True,
        }

        return render(request, 'admin/dashboard.html', context)
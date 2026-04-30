from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.db.models import Sum, Count, Max, Q
from django.db.models.functions import TruncDay
from django.contrib import messages
from datetime import timedelta
import json
import random
import string


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

        # ── Customer insights ─────────────────────────────────────────────────
        buyer_counts = (
            paid.filter(user__isnull=False)
            .values('user')
            .annotate(n=Count('id'))
        )
        returning_customers = buyer_counts.filter(n__gte=2).count()
        new_this_month      = User.objects.filter(is_staff=False, date_joined__date__gte=month_start).count()

        # ── Top buyers ────────────────────────────────────────────────────────
        top_buyers = (
            paid.filter(user__isnull=False)
            .values('user__id', 'user__email', 'user__first_name', 'user__last_name')
            .annotate(
                order_count=Count('id'),
                total_spent=Sum('total'),
                last_order=Max('created_at'),
            )
            .order_by('-total_spent')[:8]
        )

        # ── Revenue chart — last 7 days ───────────────────────────────────────
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
            'total_revenue':        f'₦{total_revenue:,.0f}',
            'today_revenue':        f'₦{today_revenue:,.0f}',
            'month_revenue':        f'₦{month_revenue:,.0f}',
            'total_orders':         total_orders,
            'today_orders':         today_orders,
            'pending_orders':       pending_orders,
            'total_customers':      total_customers,
            'total_products':       total_products,
            'low_stock':            low_stock,
            'pending_reviews':      pending_reviews,
            'returning_customers':  returning_customers,
            'new_this_month':       new_this_month,

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
            'top_buyers':         top_buyers,
            'low_stock_products': low_stock_products,

            # Admin context
            'title': 'Dashboard',
            'has_permission': True,
        }

        return render(request, 'admin/dashboard.html', context)


@method_decorator(staff_member_required, name='dispatch')
class InventoryStatusView(View):

    def get(self, request):
        from apps.products.models import Product

        search = request.GET.get('q', '').strip()
        status = request.GET.get('status', '')

        products = Product.objects.select_related('category').order_by('stock_count')

        if search:
            products = products.filter(name__icontains=search)

        if status == 'out':
            products = products.filter(stock_count=0)
        elif status == 'low':
            products = products.filter(stock_count__gt=0, stock_count__lte=5)
        elif status == 'in':
            products = products.filter(stock_count__gt=5)

        total      = Product.objects.count()
        out_of_stock = Product.objects.filter(stock_count=0).count()
        low_stock  = Product.objects.filter(stock_count__gt=0, stock_count__lte=5).count()
        in_stock   = Product.objects.filter(stock_count__gt=5).count()

        context = {
            'title':        'Inventory Status',
            'has_permission': True,
            'products':     products,
            'search':       search,
            'status_filter': status,
            'total':        total,
            'out_of_stock': out_of_stock,
            'low_stock':    low_stock,
            'in_stock':     in_stock,
        }
        return render(request, 'admin/inventory.html', context)


@method_decorator(staff_member_required, name='dispatch')
class CustomersView(View):

    def get(self, request):
        from apps.orders.models import Order
        from apps.users.models import User

        search = request.GET.get('q', '').strip()
        tier   = request.GET.get('tier', '')

        # All paid orders grouped by user, giving us spend + order count
        buyer_stats = (
            Order.objects.filter(payment_status='paid', user__isnull=False)
            .values('user_id')
            .annotate(
                order_count=Count('id'),
                total_spent=Sum('total'),
                last_order=Max('created_at'),
            )
        )
        stats_by_user = {row['user_id']: row for row in buyer_stats}

        customers = User.objects.filter(is_staff=False).order_by('-date_joined')

        if search:
            customers = customers.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        # Attach stats and tier to each customer
        enriched = []
        for c in customers:
            stats      = stats_by_user.get(c.id, {})
            n_orders   = stats.get('order_count', 0)
            spent      = stats.get('total_spent') or 0
            last_order = stats.get('last_order')

            if n_orders == 0:
                customer_tier = 'no-orders'
            elif n_orders == 1:
                customer_tier = 'new'
            elif n_orders <= 4:
                customer_tier = 'returning'
            else:
                customer_tier = 'vip'

            if tier and customer_tier != tier:
                continue

            enriched.append({
                'user':       c,
                'order_count': n_orders,
                'total_spent': spent,
                'last_order':  last_order,
                'tier':        customer_tier,
            })

        # Summary counts
        all_stats    = list(stats_by_user.values())
        vip_count    = sum(1 for s in all_stats if s['order_count'] >= 5)
        ret_count    = sum(1 for s in all_stats if 2 <= s['order_count'] <= 4)
        new_count    = sum(1 for s in all_stats if s['order_count'] == 1)
        no_ord_count = User.objects.filter(is_staff=False).count() - len(stats_by_user)

        context = {
            'title':          'Customers',
            'has_permission': True,
            'customers':      enriched,
            'search':         search,
            'tier_filter':    tier,
            'vip_count':      vip_count,
            'ret_count':      ret_count,
            'new_count':      new_count,
            'no_ord_count':   no_ord_count,
            'total_count':    User.objects.filter(is_staff=False).count(),
        }
        return render(request, 'admin/customers.html', context)


@method_decorator(staff_member_required, name='dispatch')
class CustomerEmailView(View):

    def _get_user(self, user_id):
        from apps.users.models import User
        return get_object_or_404(User, pk=user_id, is_staff=False)

    def get(self, request, user_id):
        from apps.core.admin_site import softlifee_admin
        customer = self._get_user(user_id)
        context = {
            **softlifee_admin.each_context(request),
            'title':    f'Email {customer.email}',
            'customer': customer,
        }
        return render(request, 'admin/customer_email.html', context)

    def post(self, request, user_id):
        customer = self._get_user(user_id)
        subject  = request.POST.get('subject', '').strip()
        body     = request.POST.get('body', '').strip()

        if not subject or not body:
            messages.error(request, 'Subject and message are required.')
            return redirect(f'/admin/customers/{user_id}/email/')

        try:
            from apps.core.emails import send_email
            send_email(
                subject=subject,
                to_email=customer.email,
                template='admin_message',
                context={
                    'first_name': customer.first_name or 'there',
                    'body_html':  body,
                },
            )
            messages.success(request, f'Email sent to {customer.email}.')
        except Exception as e:
            messages.error(request, f'Failed to send email: {e}')

        return redirect('/admin/customers/')


@method_decorator(staff_member_required, name='dispatch')
class CustomerDiscountView(View):

    def _get_user(self, user_id):
        from apps.users.models import User
        return get_object_or_404(User, pk=user_id, is_staff=False)

    def get(self, request, user_id):
        from apps.core.admin_site import softlifee_admin
        customer = self._get_user(user_id)
        context = {
            **softlifee_admin.each_context(request),
            'title':    f'Give Discount to {customer.first_name or customer.email}',
            'customer': customer,
        }
        return render(request, 'admin/customer_discount.html', context)

    def post(self, request, user_id):
        customer      = self._get_user(user_id)
        discount_type = request.POST.get('discount_type', 'percentage')
        value         = request.POST.get('value', '').strip()
        minimum_order = request.POST.get('minimum_order', '0').strip() or '0'
        days_valid    = int(request.POST.get('days_valid', '30') or '30')
        send_email_flag = request.POST.get('send_email') == '1'

        if not value:
            messages.error(request, 'Discount value is required.')
            return redirect(f'/admin/customers/{user_id}/discount/')

        from apps.orders.discount import DiscountCode

        # Generate a human-friendly personal code
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        name   = (customer.first_name or 'CUST').upper().replace(' ', '')[:6]
        code   = f'{name}-{suffix}'

        DiscountCode.objects.create(
            code          = code,
            discount_type = discount_type,
            value         = value,
            minimum_order = minimum_order,
            valid_from    = timezone.now(),
            valid_until   = timezone.now() + timedelta(days=days_valid),
            usage_limit   = 1,
            per_user_limit= 1,
            is_active     = True,
        )

        if send_email_flag:
            try:
                from apps.core.emails import send_email
                from django.conf import settings as dj_settings
                label = f'{value}%' if discount_type == 'percentage' else f'₦{float(value):,.0f}'
                send_email(
                    subject=f'A special discount just for you — {label} off 🎁',
                    to_email=customer.email,
                    template='discount_gift',
                    context={
                        'first_name':     customer.first_name or 'there',
                        'code':           code,
                        'discount_label': label,
                        'minimum_order':  float(minimum_order),
                        'valid_days':     days_valid,
                        'shop_url':       f'{dj_settings.FRONTEND_URL}/shop',
                    },
                )
            except Exception as e:
                messages.warning(request, f'Discount created but email failed: {e}')
                return redirect('/admin/customers/')

        messages.success(request, f'Discount code "{code}" created for {customer.email}.')
        return redirect('/admin/customers/')
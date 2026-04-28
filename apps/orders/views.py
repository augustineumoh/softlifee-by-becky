import hmac
import hashlib
import json
import requests as req
from decimal import Decimal

from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.products.models import Product
from apps.core.throttles import CheckoutThrottle
from .models import Order, OrderItem
from .serializers import OrderCreateSerializer, OrderSerializer


# ── Delivery fee calculator ───────────────────────────────────────────────────
DELIVERY_RATES = {
    'Lagos':   Decimal('1500'),
    'Ogun':    Decimal('2000'),
    'Oyo':     Decimal('2500'),
    'Osun':    Decimal('2500'),
    'Ekiti':   Decimal('2500'),
}
FREE_DELIVERY_THRESHOLD = Decimal('50000')
DEFAULT_DELIVERY        = Decimal('3500')

def get_delivery_fee(state: str, subtotal: Decimal) -> Decimal:
    if subtotal >= FREE_DELIVERY_THRESHOLD:
        return Decimal('0')
    return DELIVERY_RATES.get(state, DEFAULT_DELIVERY)


# ── Create Order ──────────────────────────────────────────────────────────────
class CreateOrderView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes   = [CheckoutThrottle]

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data  = serializer.validated_data
        items = data['items']

        # Resolve products + calculate subtotal
        order_items_data = []
        subtotal = Decimal('0')

        for item_data in items:
            try:
                product = Product.objects.get(slug=item_data['product_slug'], is_active=True)
            except Product.DoesNotExist:
                return Response(
                    {'error': f"Product '{item_data['product_slug']}' not found."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get primary image URL
            primary_img = product.images.filter(is_primary=True).first() or product.images.first()
            img_url = ''
            if primary_img:
                try:
                    img_url = primary_img.image.url
                except Exception:
                    img_url = ''

            item_subtotal = product.price * item_data['quantity']
            subtotal     += item_subtotal

            order_items_data.append({
                'product':       product,
                'product_name':  product.name,
                'product_price': product.price,
                'product_image': img_url,
                'color_variant': item_data.get('color_variant', ''),
                'size_variant':  item_data.get('size_variant', ''),
                'quantity':      item_data['quantity'],
                'subtotal':      item_subtotal,
            })

        # Handle discount code safely
        discount_amount   = Decimal('0')
        discount_code_str = data.get('discount_code', '').strip().upper()
        applied_code      = None

        if discount_code_str:
            try:
                from .discount import DiscountCode
                applied_code = DiscountCode.objects.get(code=discount_code_str)
                valid, msg   = applied_code.is_valid(user=request.user, subtotal=subtotal)
                if valid:
                    discount_amount = applied_code.calculate_discount(subtotal)
                else:
                    return Response({'error': msg}, status=status.HTTP_400_BAD_REQUEST)
            except Exception:
                pass  # Ignore discount errors — don't block checkout

        delivery_fee = get_delivery_fee(data['delivery_state'], subtotal - discount_amount)
        total        = subtotal - discount_amount + delivery_fee
        payment_method = data['payment_method']

        # Build order kwargs — only include discount fields if columns exist
        order_kwargs = dict(
            user            = request.user if request.user.is_authenticated else None,
            customer_name   = data['customer_name'],
            customer_email  = data['customer_email'],
            customer_phone  = data['customer_phone'],
            delivery_address = data['delivery_address'],
            delivery_city   = data['delivery_city'],
            delivery_state  = data['delivery_state'],
            delivery_notes  = data.get('delivery_notes', ''),
            subtotal        = subtotal,
            delivery_fee    = delivery_fee,
            total           = total,
            payment_method  = payment_method,
            payment_status  = 'pending',
        )

        # Try to add discount fields — if column doesn't exist yet, skip
        try:
            from django.db import connection
            columns = [col.name for col in connection.introspection.get_table_description(
                connection.cursor(), 'orders_order'
            )]
            if 'discount_code' in columns:
                order_kwargs['discount_code']   = discount_code_str
                order_kwargs['discount_amount'] = discount_amount
        except Exception:
            pass

        # Create order
        order = Order.objects.create(**order_kwargs)

        # Create order items
        for item_data in order_items_data:
            OrderItem.objects.create(order=order, **item_data)

        # Mark discount code as used
        if applied_code:
            try:
                applied_code.apply(
                    user=request.user if request.user.is_authenticated else None,
                    order=order
                )
            except Exception:
                pass

        # If Pay on Delivery
        if payment_method == 'pod':
            order.status         = 'confirmed'
            order.payment_status = 'pending'
            order.save(update_fields=['status', 'payment_status'])

            # Send confirmation email
            try:
                from apps.core.emails import send_order_confirmation_email
                send_order_confirmation_email(order)
            except Exception:
                pass

            return Response({
                'order':          OrderSerializer(order).data,
                'payment_method': 'pod',
                'message':        'Order placed successfully. Pay on delivery.',
            }, status=status.HTTP_201_CREATED)

        # For card/transfer/ussd — initialise Paystack
        paystack_response = req.post(
            'https://api.paystack.co/transaction/initialize',
            headers={
                'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
                'Content-Type':  'application/json',
            },
            json={
                'email':     data['customer_email'],
                'amount':    int(total * 100),
                'reference': order.order_number,
                'metadata':  {
                    'order_number':   order.order_number,
                    'customer_name':  data['customer_name'],
                    'delivery_state': data['delivery_state'],
                },
                'callback_url': f"{settings.FRONTEND_URL}/order-success",
            }
        )

        if paystack_response.status_code != 200:
            order.delete()
            return Response(
                {'error': 'Could not initialise payment. Please try again.'},
                status=status.HTTP_502_BAD_GATEWAY
            )

        ps_data = paystack_response.json()['data']
        order.paystack_ref = ps_data['reference']
        order.save(update_fields=['paystack_ref'])

        return Response({
            'order':        OrderSerializer(order).data,
            'payment_url':  ps_data['authorization_url'],
            'paystack_ref': ps_data['reference'],
        }, status=status.HTTP_201_CREATED)


# ── Paystack Webhook ──────────────────────────────────────────────────────────
@method_decorator(csrf_exempt, name='dispatch')
class PaystackWebhookView(APIView):
    permission_classes     = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        paystack_sig = request.headers.get('x-paystack-signature', '')
        body         = request.body
        expected_sig = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
            body,
            digestmod=hashlib.sha512
        ).hexdigest()

        if not hmac.compare_digest(paystack_sig, expected_sig):
            return Response({'error': 'Invalid signature.'}, status=status.HTTP_400_BAD_REQUEST)

        event = json.loads(body)

        if event.get('event') == 'charge.success':
            data      = event['data']
            reference = data.get('reference')
            try:
                order = Order.objects.get(paystack_ref=reference)
                if order.payment_status != 'paid':
                    order.payment_status  = 'paid'
                    order.status          = 'confirmed'
                    order.paystack_txn_id = data.get('id', '')
                    order.paid_at         = timezone.now()
                    order.save(update_fields=[
                        'payment_status', 'status', 'paystack_txn_id', 'paid_at'
                    ])
                    try:
                        from apps.core.emails import send_order_confirmation_email
                        send_order_confirmation_email(order)
                    except Exception:
                        pass
            except Order.DoesNotExist:
                pass

        return Response({'status': 'ok'})


# ── Verify Payment ────────────────────────────────────────────────────────────
class VerifyPaymentView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, reference):
        try:
            order = Order.objects.get(paystack_ref=reference)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        ps_resp = req.get(
            f'https://api.paystack.co/transaction/verify/{reference}',
            headers={'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'}
        )

        if ps_resp.status_code == 200:
            ps_data = ps_resp.json()['data']
            if ps_data['status'] == 'success' and order.payment_status != 'paid':
                order.payment_status  = 'paid'
                order.status          = 'confirmed'
                order.paystack_txn_id = str(ps_data.get('id', ''))
                order.paid_at         = timezone.now()
                order.save(update_fields=[
                    'payment_status', 'status', 'paystack_txn_id', 'paid_at'
                ])
                try:
                    from apps.core.emails import send_order_confirmation_email
                    send_order_confirmation_email(order)
                except Exception:
                    pass

        return Response(OrderSerializer(order).data)


# ── Order history ─────────────────────────────────────────────────────────────
class OrderListView(generics.ListAPIView):
    serializer_class   = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items').order_by('-created_at')


# ── Single order ──────────────────────────────────────────────────────────────
class OrderDetailView(generics.RetrieveAPIView):
    serializer_class   = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')
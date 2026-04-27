from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.core.throttles import ReturnRequestThrottle

from .models import Order, OrderItem, ReturnRequest, ReturnItem
from .return_serializers import (
    ReturnRequestSerializer, ReturnRequestCreateSerializer, AdminReturnUpdateSerializer
)


class CreateReturnRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes   = [ReturnRequestThrottle]

    def post(self, request):
        serializer = ReturnRequestCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            order = Order.objects.get(
                id=data['order_id'],
                user=request.user,
                status='delivered',
                payment_status='paid',
            )
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found or not eligible for return. Only paid, delivered orders can be returned.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if ReturnRequest.objects.filter(order=order, status__in=['pending', 'approved']).exists():
            return Response(
                {'error': 'An active return request already exists for this order.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order_item_ids = set(order.items.values_list('id', flat=True))
        return_items_to_create = []

        for item_data in data['items']:
            oi_id = item_data['order_item_id']
            if oi_id not in order_item_ids:
                return Response(
                    {'error': f'Item {oi_id} does not belong to this order.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            order_item = get_object_or_404(OrderItem, id=oi_id)
            if item_data['quantity'] > order_item.quantity:
                return Response(
                    {'error': f'Return quantity for "{order_item.product_name}" cannot exceed ordered quantity ({order_item.quantity}).'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return_items_to_create.append({
                'order_item': order_item,
                'quantity':   item_data['quantity'],
            })

        return_request = ReturnRequest.objects.create(
            order       = order,
            user        = request.user,
            reason      = data['reason'],
            description = data['description'],
        )
        for ri in return_items_to_create:
            ReturnItem.objects.create(
                return_request=return_request,
                order_item=ri['order_item'],
                quantity=ri['quantity'],
            )

        try:
            from apps.core.emails import send_email
            from django.conf import settings
            send_email(
                subject  = f'Return Request Received — {return_request.return_number}',
                to_email = order.customer_email,
                template = 'return_request',
                context  = {
                    'order':          order,
                    'return_request': return_request,
                    'track_url':      f"{settings.FRONTEND_URL}/account/returns",
                }
            )
        except Exception:
            pass

        return Response(
            ReturnRequestSerializer(return_request).data,
            status=status.HTTP_201_CREATED
        )


class MyReturnRequestsView(generics.ListAPIView):
    serializer_class   = ReturnRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReturnRequest.objects.filter(
            user=self.request.user
        ).prefetch_related('items__order_item').select_related('order')


class ReturnRequestDetailView(generics.RetrieveAPIView):
    serializer_class   = ReturnRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReturnRequest.objects.filter(
            user=self.request.user
        ).prefetch_related('items__order_item').select_related('order')


class AdminReturnListView(generics.ListAPIView):
    serializer_class   = ReturnRequestSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        qs = ReturnRequest.objects.all().prefetch_related(
            'items__order_item'
        ).select_related('order', 'user')
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


class AdminReturnUpdateView(generics.UpdateAPIView):
    serializer_class   = AdminReturnUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset           = ReturnRequest.objects.all()
    http_method_names  = ['patch']

    def perform_update(self, serializer):
        instance = serializer.save()
        try:
            from apps.core.emails import send_email
            from django.conf import settings
            status_messages = {
                'approved':  'Your return request has been approved',
                'rejected':  'Your return request has been reviewed',
                'completed': 'Your return has been completed',
            }
            if instance.status in status_messages:
                send_email(
                    subject  = f'Return Update — {instance.return_number}',
                    to_email = instance.order.customer_email,
                    template = 'return_update',
                    context  = {
                        'return_request': instance,
                        'order':          instance.order,
                        'message':        status_messages[instance.status],
                        'track_url':      f"{settings.FRONTEND_URL}/account/returns",
                    }
                )
        except Exception:
            pass

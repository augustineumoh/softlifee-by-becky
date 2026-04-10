from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from decimal import Decimal
from .discount import DiscountCode


class ValidateDiscountCodeView(APIView):
    """
    POST /api/v1/orders/discount/validate/
    Body: { "code": "SAVE10", "subtotal": 25000 }
    Returns discount amount if valid.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        code_str = request.data.get('code', '').strip().upper()
        subtotal = Decimal(str(request.data.get('subtotal', 0)))

        if not code_str:
            return Response({'error': 'Code is required.'}, status=400)

        try:
            code = DiscountCode.objects.get(code=code_str)
        except DiscountCode.DoesNotExist:
            return Response({'error': 'Invalid discount code.'}, status=404)

        valid, message = code.is_valid(user=request.user, subtotal=subtotal)
        if not valid:
            return Response({'error': message}, status=400)

        discount_amount = code.calculate_discount(subtotal)

        return Response({
            'valid':           True,
            'code':            code.code,
            'discount_type':   code.discount_type,
            'value':           str(code.value),
            'discount_amount': str(discount_amount),
            'new_subtotal':    str(subtotal - discount_amount),
            'message':         f'Code applied! You save ₦{discount_amount:,.0f}',
        })
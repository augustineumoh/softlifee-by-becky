import uuid
from django.core.cache import cache
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import User
from apps.core.emails import send_password_reset_email


class RequestPasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response({'error': 'Email is required.'}, status=400)

        try:
            user = User.objects.get(email=email)
            # Generate a unique token, store in cache for 1 hour
            token     = str(uuid.uuid4())
            cache_key = f'password_reset_{token}'
            cache.set(cache_key, user.id, timeout=3600)

            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
            send_password_reset_email(user, reset_url)
        except User.DoesNotExist:
            pass  # Don't reveal if email exists

        return Response({
            'message': 'If an account exists with that email, a reset link has been sent.'
        })


class ConfirmPasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token        = request.data.get('token', '')
        new_password = request.data.get('new_password', '')
        confirm      = request.data.get('confirm_password', '')

        if not token or not new_password:
            return Response({'error': 'Token and new password are required.'}, status=400)

        if new_password != confirm:
            return Response({'error': 'Passwords do not match.'}, status=400)

        if len(new_password) < 8:
            return Response({'error': 'Password must be at least 8 characters.'}, status=400)

        cache_key = f'password_reset_{token}'
        user_id   = cache.get(cache_key)

        if not user_id:
            return Response({'error': 'Reset link is invalid or has expired.'}, status=400)

        try:
            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()
            cache.delete(cache_key)  # Invalidate token after use
            return Response({'message': 'Password reset successfully. You can now log in.'})
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)
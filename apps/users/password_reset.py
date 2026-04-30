from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.conf import settings

from .models import User, PasswordResetToken
from apps.core.emails import send_password_reset_email


class RequestPasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response({'error': 'Email is required.'}, status=400)

        try:
            user = User.objects.get(email=email)
            # Invalidate any existing unused tokens for this user
            PasswordResetToken.objects.filter(user=user, used=False).update(used=True)

            token_obj = PasswordResetToken.objects.create(
                user=user,
                expires_at=timezone.now() + timedelta(hours=1),
            )
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token_obj.token}"
            send_password_reset_email(user, reset_url)
        except User.DoesNotExist:
            pass  # Don't reveal whether the email exists

        return Response({
            'message': 'If an account exists with that email, a reset link has been sent.'
        })


class ConfirmPasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token_str    = request.data.get('token', '').strip()
        new_password = request.data.get('new_password', '')
        confirm      = request.data.get('confirm_password', '')

        if not token_str or not new_password:
            return Response({'error': 'Token and new password are required.'}, status=400)

        if new_password != confirm:
            return Response({'error': 'Passwords do not match.'}, status=400)

        if len(new_password) < 8:
            return Response({'error': 'Password must be at least 8 characters.'}, status=400)

        try:
            token_obj = PasswordResetToken.objects.select_related('user').get(token=token_str)
        except (PasswordResetToken.DoesNotExist, ValueError):
            return Response({'error': 'Reset link is invalid or has expired.'}, status=400)

        if not token_obj.is_valid():
            return Response({'error': 'Reset link is invalid or has expired.'}, status=400)

        user = token_obj.user
        user.set_password(new_password)
        user.save()

        token_obj.used = True
        token_obj.save(update_fields=['used'])

        return Response({'message': 'Password reset successfully. You can now log in.'})

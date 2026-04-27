from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import User, Address, ReferralUse
from apps.core.emails import send_welcome_email
from apps.core.rate_limit import rate_limit
from apps.core.throttles import RegisterThrottle, LoginThrottle
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    ChangePasswordSerializer, AddressSerializer, get_tokens_for_user
)


# ── Register ──────────────────────────────────────────────────────────────────
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes   = [RegisterThrottle]

    @rate_limit(key='register', limit=3, period=3600)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user   = serializer.save()
            tokens = get_tokens_for_user(user)
            send_welcome_email(user)
            return Response({
                'message': 'Account created successfully.',
                'user':    UserSerializer(user).data,
                'tokens':  tokens,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Login ─────────────────────────────────────────────────────────────────────
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes   = [LoginThrottle]

    @rate_limit(key='login', limit=5, period=300)
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user   = serializer.validated_data['user']
            tokens = get_tokens_for_user(user)
            return Response({
                'message': 'Login successful.',
                'user':    UserSerializer(user).data,
                'tokens':  tokens,
            })
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


# ── Logout ────────────────────────────────────────────────────────────────────
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'})
        except Exception:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


# ── Profile — GET + PATCH ─────────────────────────────────────────────────────
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class   = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


# ── Avatar upload ─────────────────────────────────────────────────────────────
class AvatarUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if 'avatar' not in request.FILES:
            return Response({'error': 'No image provided.'}, status=status.HTTP_400_BAD_REQUEST)
        user.avatar = request.FILES['avatar']
        user.save()
        return Response({
            'message': 'Avatar updated.',
            'avatar':  request.build_absolute_uri(user.avatar.url) if user.avatar else None,
        })


# ── Change Password ───────────────────────────────────────────────────────────
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password changed successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Addresses ─────────────────────────────────────────────────────────────────
class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class   = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


# ── Referral info ─────────────────────────────────────────────────────────────
class ReferralInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user     = request.user
        referrals = ReferralUse.objects.filter(referrer=user).select_related('referred')
        referred_users = [
            {
                'email':      r.referred.email,
                'first_name': r.referred.first_name,
                'joined_at':  r.created_at,
            }
            for r in referrals
        ]
        return Response({
            'referral_code':  user.referral_code,
            'referral_link':  f"{request.build_absolute_uri('/')[:-1]}/register?ref={user.referral_code}",
            'total_referrals': len(referred_users),
            'referred_users': referred_users,
        })


# ── Google OAuth callback ─────────────────────────────────────────────────────
class GoogleAuthView(APIView):
    """
    Receives the access_token from the frontend after Google OAuth popup.
    Exchanges it for our own JWT tokens.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        import requests as req
        access_token = request.data.get('access_token')
        if not access_token:
            return Response({'error': 'access_token is required.'}, status=400)

        # Get user info from Google
        google_resp = req.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if google_resp.status_code != 200:
            return Response({'error': 'Invalid Google token.'}, status=400)

        data       = google_resp.json()
        email      = data.get('email')
        first_name = data.get('given_name', '')
        last_name  = data.get('family_name', '')

        if not email:
            return Response({'error': 'Could not retrieve email from Google.'}, status=400)

        user, created = User.objects.get_or_create(
            email=email,
            defaults={'first_name': first_name, 'last_name': last_name}
        )
        if created:
            user.set_unusable_password()
            user.save()

        tokens = get_tokens_for_user(user)
        return Response({
            'message': 'Login successful.',
            'user':    UserSerializer(user).data,
            'tokens':  tokens,
            'created': created,
        })
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, Address, ReferralUse


# ── Register ──────────────────────────────────────────────────────────────────
class RegisterSerializer(serializers.ModelSerializer):
    password      = serializers.CharField(write_only=True, min_length=8)
    password2     = serializers.CharField(write_only=True)
    referral_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'password', 'password2', 'referral_code']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        code = data.get('referral_code', '').strip().upper()
        if code:
            if not User.objects.filter(referral_code=code).exists():
                raise serializers.ValidationError({'referral_code': 'Invalid referral code.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        referral_code = validated_data.pop('referral_code', '').strip().upper()
        user = User.objects.create_user(**validated_data)
        if referral_code:
            try:
                referrer = User.objects.get(referral_code=referral_code)
                ReferralUse.objects.create(referrer=referrer, referred=user)
            except User.DoesNotExist:
                pass
        return user


# ── Login ─────────────────────────────────────────────────────────────────────
class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        request = self.context.get('request')
        user = authenticate(request, email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        if not user.is_active:
            raise serializers.ValidationError('Account is disabled.')
        data['user'] = user
        return data


# ── User Profile ──────────────────────────────────────────────────────────────
class UserSerializer(serializers.ModelSerializer):
    full_name      = serializers.ReadOnlyField()
    avatar_url     = serializers.SerializerMethodField()
    avatar         = serializers.SerializerMethodField()   # override — never return /media/ paths
    referral_count = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name',
                  'phone', 'avatar', 'avatar_url', 'referral_code',
                  'referral_count', 'date_joined']
        read_only_fields = ['id', 'email', 'referral_code', 'date_joined']

    def get_referral_count(self, obj):
        return obj.referrals_given.count()

    def _get_avatar_url(self, obj):
        """Return a working Cloudinary URL for the user's avatar."""
        if not obj.avatar:
            return None
        raw = str(obj.avatar)
        if not raw:
            return None
        # Google OAuth or any pre-built URL — return as-is
        if raw.startswith('http://') or raw.startswith('https://'):
            return raw
        # Let the storage backend (MediaCloudinaryStorage) build the URL
        try:
            url = obj.avatar.url
            if url and url.startswith('http'):
                return url
        except Exception:
            pass
        # Fallback: construct Cloudinary URL manually from stored public ID
        from django.conf import settings
        cloud = getattr(settings, 'CLOUDINARY_STORAGE', {}).get('CLOUD_NAME', '')
        if cloud:
            public_id = raw.lstrip('/')
            return f'https://res.cloudinary.com/{cloud}/image/upload/{public_id}'
        return None

    def get_avatar(self, obj):
        return self._get_avatar_url(obj)

    def get_avatar_url(self, obj):
        return self._get_avatar_url(obj)


# ── Change Password ───────────────────────────────────────────────────────────
class ChangePasswordSerializer(serializers.Serializer):
    old_password  = serializers.CharField(write_only=True)
    new_password  = serializers.CharField(write_only=True, min_length=8)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({'new_password': 'Passwords do not match.'})
        return data

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


# ── Address ───────────────────────────────────────────────────────────────────
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Address
        fields = ['id', 'label', 'full_name', 'phone', 'address',
                  'city', 'state', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# ── Token response helper ─────────────────────────────────────────────────────
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access':  str(refresh.access_token),
    }
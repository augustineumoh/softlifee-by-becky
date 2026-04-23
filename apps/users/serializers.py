from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, Address
import cloudinary


# ── Register ──────────────────────────────────────────────────────────────────
class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)


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
    full_name  = serializers.ReadOnlyField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name',
                  'phone', 'avatar', 'avatar_url', 'date_joined']
        read_only_fields = ['id', 'email', 'date_joined']

    def get_avatar_url(self, obj):
        """Return optimized Cloudinary URL for avatar."""
        if not obj.avatar:
            return None
        try:
            # Build optimized Cloudinary URL
            url = cloudinary.CloudinaryImage(str(obj.avatar)).build_url(
                width=200, height=200,
                crop='fill', gravity='face',
                fetch_format='auto', quality='auto',
            )
            return url
        except Exception:
            # Fallback to raw URL
            try:
                return obj.avatar.url
            except Exception:
                return None


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
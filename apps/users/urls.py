from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .password_reset import RequestPasswordResetView, ConfirmPasswordResetView

urlpatterns = [
    # Auth
    path('register/',         views.RegisterView.as_view(),          name='register'),
    path('login/',            views.LoginView.as_view(),             name='login'),
    path('logout/',           views.LogoutView.as_view(),            name='logout'),
    path('token/refresh/',    TokenRefreshView.as_view(),            name='token-refresh'),
    path('google/',           views.GoogleAuthView.as_view(),        name='google-auth'),

    # Password reset
    path('password-reset/',          RequestPasswordResetView.as_view(),  name='password-reset-request'),
    path('password-reset/confirm/',  ConfirmPasswordResetView.as_view(),  name='password-reset-confirm'),

    # Profile
    path('profile/',          views.ProfileView.as_view(),           name='profile'),
    path('profile/avatar/',   views.AvatarUploadView.as_view(),      name='avatar-upload'),
    path('profile/password/', views.ChangePasswordView.as_view(),    name='change-password'),

    # Addresses
    path('addresses/',           views.AddressListCreateView.as_view(), name='address-list'),
    path('addresses/<int:pk>/',  views.AddressDetailView.as_view(),    name='address-detail'),
]
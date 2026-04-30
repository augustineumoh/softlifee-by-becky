from django.urls import path
from .views import SubscribeView, UnsubscribeView

urlpatterns = [
    path('subscribe/', SubscribeView.as_view(), name='newsletter-subscribe'),
    path('unsubscribe/<uuid:token>/', UnsubscribeView.as_view(), name='newsletter-unsubscribe'),
]

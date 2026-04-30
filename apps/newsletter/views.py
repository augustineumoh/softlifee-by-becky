from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import NewsletterSubscriber
from .serializers import SubscribeSerializer
from .emails import send_welcome_newsletter_email


class SubscribeView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = 'newsletter_subscribe'

    def post(self, request):
        email = (request.data.get('email') or '').lower().strip()
        if not email:
            return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={'name': request.data.get('name', '')},
        )

        if not created and subscriber.is_active:
            return Response({'detail': 'You are already subscribed.'}, status=status.HTTP_200_OK)

        if not created and not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save(update_fields=['is_active'])

        try:
            send_welcome_newsletter_email(subscriber)
        except Exception:
            pass  # don't fail subscription if email errors

        return Response({'detail': 'Subscribed! Check your inbox for a welcome email.'}, status=status.HTTP_201_CREATED)


class UnsubscribeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        subscriber = get_object_or_404(NewsletterSubscriber, unsubscribe_token=token)
        subscriber.is_active = False
        subscriber.save(update_fields=['is_active'])
        return Response({'detail': 'You have been unsubscribed.'}, status=status.HTTP_200_OK)

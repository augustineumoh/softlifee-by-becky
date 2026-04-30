from rest_framework import serializers
from .models import NewsletterSubscriber


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email', 'name']

    def validate_email(self, value):
        return value.lower().strip()

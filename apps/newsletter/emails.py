from django.conf import settings
from apps.core.emails import send_email


def send_welcome_newsletter_email(subscriber):
    send_email(
        subject='Welcome to the Soft Lifee newsletter! 💜',
        to_email=subscriber.email,
        template='newsletter_welcome',
        context={
            'name': subscriber.name or 'there',
            'unsubscribe_url': f"{settings.FRONTEND_URL}/unsubscribe?token={subscriber.unsubscribe_token}",
            'shop_url': f"{settings.FRONTEND_URL}/shop",
        },
    )


def send_newsletter_blast(subscribers, subject, heading, body_html, cta_label, cta_url):
    """Send a newsletter to a queryset of active subscribers."""
    for sub in subscribers:
        send_email(
            subject=subject,
            to_email=sub.email,
            template='newsletter',
            context={
                'name': sub.name or 'there',
                'heading': heading,
                'body_html': body_html,
                'cta_label': cta_label,
                'cta_url': cta_url,
                'unsubscribe_url': f"{settings.FRONTEND_URL}/unsubscribe?token={sub.unsubscribe_token}",
            },
        )

import threading
import logging

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send_email_async(subject: str, to_email: str, template: str, context: dict):
    """Send email in a background thread — never blocks the caller."""
    def _send():
        try:
            send_email(subject=subject, to_email=to_email, template=template, context=context)
        except Exception as e:
            logger.error('Async email to %s failed: %s', to_email, e)

    threading.Thread(target=_send, daemon=True).start()


def send_email(subject: str, to_email: str, template: str, context: dict):
    """Generic email sender using HTML templates."""
    context.setdefault('brand_name',  'Soft Lifee by Becky')
    context.setdefault('brand_color', '#8A4FB1')
    context.setdefault('frontend_url', settings.FRONTEND_URL)

    html_content  = render_to_string(f'emails/{template}.html', context)
    text_content  = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject   = subject,
        body      = text_content,
        from_email= settings.DEFAULT_FROM_EMAIL,
        to        = [to_email],
    )
    email.attach_alternative(html_content, 'text/html')
    email.send(fail_silently=False)


# ── Specific email senders ────────────────────────────────────────────────────

def send_welcome_email(user):
    send_email(
        subject  = 'Welcome to Soft Lifee by Becky! 🎉',
        to_email = user.email,
        template = 'welcome',
        context  = {
            'first_name':   user.first_name or 'there',
            'shop_url':     f"{settings.FRONTEND_URL}/shop",
            'account_url':  f"{settings.FRONTEND_URL}/account",
        }
    )


def send_order_confirmation_email(order):
    send_email(
        subject  = f'Order Confirmed — {order.order_number} ✅',
        to_email = order.customer_email,
        template = 'order_confirmation',
        context  = {
            'order':        order,
            'items':        order.items.all(),
            'track_url':    f"{settings.FRONTEND_URL}/account/orders",
        }
    )


def send_order_status_email(order):
    status_messages = {
        'processing': ('Your order is being processed 📦', 'order_processing'),
        'shipped':    ('Your order is on its way! 🚚',     'order_shipped'),
        'delivered':  ('Your order has been delivered! 🎉', 'order_delivered'),
        'cancelled':  ('Your order has been cancelled',     'order_cancelled'),
    }
    subject_text, template = status_messages.get(
        order.status, ('Order Update', 'order_update')
    )
    send_email(
        subject  = f'{subject_text} — {order.order_number}',
        to_email = order.customer_email,
        template = template,
        context  = {
            'order':     order,
            'track_url': f"{settings.FRONTEND_URL}/account/orders",
        }
    )


def send_password_reset_email(user, reset_url: str):
    send_email(
        subject  = 'Reset Your Password — Soft Lifee',
        to_email = user.email,
        template = 'password_reset',
        context  = {
            'first_name': user.first_name or 'there',
            'reset_url':  reset_url,
        }
    )


def send_low_stock_alert(product):
    send_email(
        subject  = f'⚠️ Low Stock Alert — {product.name}',
        to_email = settings.ADMIN_EMAIL,
        template = 'low_stock',
        context  = {
            'product':   product,
            'admin_url': f"{settings.BACKEND_URL}/admin/products/product/{product.id}/change/",
        }
    )
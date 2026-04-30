from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django.http import HttpRequest
from django.contrib.admin import ModelAdmin, action

from apps.core.admin_site import softlifee_admin
from .models import NewsletterSubscriber
from .emails import send_newsletter_blast


class NewsletterSubscriberAdmin(ModelAdmin):
    list_display = ['email', 'name', 'is_active', 'subscribed_at']
    list_filter = ['is_active']
    search_fields = ['email', 'name']
    readonly_fields = ['unsubscribe_token', 'subscribed_at']
    actions = ['reactivate_subscribers', 'deactivate_subscribers']

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                'send-newsletter/',
                softlifee_admin.admin_view(self.send_newsletter_view),
                name='send_newsletter',
            ),
        ]
        return custom + urls

    def send_newsletter_view(self, request: HttpRequest):
        if request.method == 'POST':
            subject = request.POST.get('subject', '').strip()
            heading = request.POST.get('heading', '').strip()
            body_html = request.POST.get('body_html', '').strip()
            cta_label = request.POST.get('cta_label', 'Shop Now').strip()
            cta_url = request.POST.get('cta_url', '').strip()

            if not subject or not heading or not body_html:
                messages.error(request, 'Subject, heading, and body are required.')
                return redirect('softlifee_admin:send_newsletter')

            subscribers = NewsletterSubscriber.objects.filter(is_active=True)
            count = subscribers.count()

            if count == 0:
                messages.warning(request, 'No active subscribers to send to.')
                return redirect('softlifee_admin:send_newsletter')

            try:
                send_newsletter_blast(subscribers, subject, heading, body_html, cta_label, cta_url)
                messages.success(request, f'Newsletter sent to {count} subscriber(s).')
            except Exception as e:
                messages.error(request, f'Error sending newsletter: {e}')

            return redirect('softlifee_admin:newsletter_newslettersubscriber_changelist')

        active_count = NewsletterSubscriber.objects.filter(is_active=True).count()
        context = {
            **softlifee_admin.each_context(request),
            'title': 'Send Newsletter',
            'active_count': active_count,
        }
        return render(request, 'admin/send_newsletter.html', context)

    @action(description='Re-activate selected subscribers')
    def reactivate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} subscriber(s) reactivated.')

    @action(description='Deactivate selected subscribers')
    def deactivate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} subscriber(s) deactivated.')


softlifee_admin.register(NewsletterSubscriber, NewsletterSubscriberAdmin)

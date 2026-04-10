from django.contrib import admin
from django.urls import path
from .admin_views import AdminDashboardView


class SoftLifeeAdminSite(admin.AdminSite):
    site_header  = 'Soft Lifee by Becky'
    site_title   = 'Soft Lifee Admin'
    index_title  = 'Dashboard'

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('', self.admin_view(AdminDashboardView.as_view()), name='index'),
        ]
        return custom + urls


# Replace Django's default admin site
softlifee_admin = SoftLifeeAdminSite(name='softlifee_admin')
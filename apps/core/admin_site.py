from django.contrib import admin
from django.urls import path
from .admin_views import (
    AdminDashboardView, InventoryStatusView,
    CustomersView, CustomerEmailView, CustomerDiscountView,
)


class SoftLifeeAdminSite(admin.AdminSite):
    site_header  = 'Soft Lifee by Becky'
    site_title   = 'Soft Lifee Admin'
    index_title  = 'Dashboard'

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('',                                          self.admin_view(AdminDashboardView.as_view()),    name='index'),
            path('inventory/',                                self.admin_view(InventoryStatusView.as_view()),   name='inventory'),
            path('customers/',                                self.admin_view(CustomersView.as_view()),         name='customers'),
            path('customers/<int:user_id>/email/',            self.admin_view(CustomerEmailView.as_view()),     name='customer_email'),
            path('customers/<int:user_id>/discount/',         self.admin_view(CustomerDiscountView.as_view()),  name='customer_discount'),
        ]
        return custom + urls


# Replace Django's default admin site
softlifee_admin = SoftLifeeAdminSite(name='softlifee_admin')
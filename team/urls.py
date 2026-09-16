from django.urls import path
from . import views

app_name = 'team'

urlpatterns = [
    # Basic Pages
    path('', views.home_view, name='home'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('coaches/', views.coaches_view, name='coaches'),
    path('contact/', views.contact_view, name='contact'),
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('cookies/', views.cookies_view, name='cookies'),

    # Staff/Admin Portal
    path('dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('approvals/', views.approval_dashboard, name='approval_dashboard'),
    path('manage-roles/', views.manage_roles_view, name='manage_roles'),
]

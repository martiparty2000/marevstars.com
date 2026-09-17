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

    # Public support chat
    path('support/api/start/', views.support_start, name='support_start'),
    path('support/api/thread/<uuid:public_id>/', views.support_thread, name='support_thread'),
    path('support/api/thread/<uuid:public_id>/message/', views.support_message, name='support_message'),
    path('support/api/thread/<uuid:public_id>/escalate/', views.support_escalate, name='support_escalate'),

    # Staff-only support portal
    path('support/login/', views.support_login, name='support_login'),
    path('support/logout/', views.support_logout, name='support_logout'),
    path('support/', views.support_dashboard, name='support_dashboard'),
    path('support/ticket/<uuid:public_id>/', views.support_ticket_detail, name='support_ticket_detail'),

    # Staff/Admin Portal
    path('dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('approvals/', views.approval_dashboard, name='approval_dashboard'),
    path('manage-roles/', views.manage_roles_view, name='manage_roles'),
]

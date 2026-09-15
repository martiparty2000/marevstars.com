from django.urls import path
from . import views

app_name = 'team'

urlpatterns = [
    # Basic Pages
    path('', views.home_view, name='home'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('coaches/', views.coaches_view, name='coaches'),
    path('contact/', views.contact_view, name='contact'),

    # Temporary admin creation endpoint
    path('init-admin/<str:secret>/', views.create_admin_view, name='create_admin'),

    # Staff/Admin Portal
    path('dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('approvals/', views.approval_dashboard, name='approval_dashboard'),
    path('manage-roles/', views.manage_roles_view, name='manage_roles'),
]
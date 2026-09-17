from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ApprovalLog, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    list_display = ('username', 'full_name', 'role', 'is_approved', 'egn')
    fieldsets = list(UserAdmin.fieldsets) + [
        ('Custom Profile Info', {
            'fields': (
                'role', 'is_approved', 'egn', 'full_name',
                'date_of_birth', 'child_egn', 'child_full_name',
            )
        }),
    ]


@admin.register(ApprovalLog)
class ApprovalLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'target', 'actor', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('target__full_name', 'actor__full_name', 'note')

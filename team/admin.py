from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    list_display = ('username', 'full_name', 'role', 'is_approved', 'egn')
    
    # Change list() to tuple() to satisfy Django's internal requirements
    # Force the fieldsets into a list to bypass type-checking issues
    fieldsets = list(UserAdmin.fieldsets) + [
        ('Custom Profile Info', {
            'fields': (
                'role', 'is_approved', 'egn', 'full_name', 
                'date_of_birth', 'child_egn', 'child_full_name'
            )
        }),
    ]
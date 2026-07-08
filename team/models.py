from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from typing import ClassVar
from django.utils import timezone

class UserProfileManager(BaseUserManager):
    def create_user(self, egn, full_name, email, password=None, **extra_fields):
        if not egn:
            raise ValueError('The EGN field must be set')
        email = self.normalize_email(email)
        
        extra_fields.setdefault('username', egn)
        
        user = self.model(egn=egn, full_name=full_name, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, egn, full_name, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_approved', True)
        extra_fields.setdefault('role', 'owner')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(egn, full_name, email, password, **extra_fields)


class UserProfile(AbstractUser):
    ROLE_CHOICES = (
        ('player', 'Player'),
        ('coach', 'Coach'),
        ('head_coach', 'Head Coach'),
        ('owner', 'Owner'),
    )
    # one canonical role field with default and choices
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='player')
    # ... rest of your fields
    
    # Custom fields with explicit type definitions for Pylance
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    full_name = models.CharField(max_length=255, help_text="Your 3 names")
    egn = models.CharField(max_length=10, unique=True, verbose_name="ЕГН")
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True, max_length=500)
    is_approved = models.BooleanField(default=False)

    # Parent linking fields
    child_egn = models.CharField(max_length=10, blank=True, null=True)
    child_full_name = models.CharField(max_length=255, blank=True, null=True)

    # Link the custom manager cleanly
    objects: ClassVar[UserProfileManager] = UserProfileManager() # type: ignore

    USERNAME_FIELD = 'egn'
    REQUIRED_FIELDS = ['full_name', 'email']

    class Meta:
        db_table = 'team_userprofile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self) -> str:
        role_display = getattr(self, 'get_role_display', lambda: self.role)()
        return f"{self.full_name} ({role_display})"


class ApprovalLog(models.Model):
    ACTION_CHOICES = (
        ('approve', 'Approve'),
        ('deny', 'Deny'),
        ('delete', 'Delete'),
        ('role_change', 'Role Change'),
    )
    actor = models.ForeignKey('team.UserProfile', related_name='actions', on_delete=models.SET_NULL, null=True, blank=True)
    target = models.ForeignKey('team.UserProfile', related_name='target_logs', on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    note = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def get_action_display(self) -> str:
        return dict(self.ACTION_CHOICES).get(self.action, self.action)

    def __str__(self) -> str:
        actor = self.actor.full_name if self.actor else 'System'
        action = self.get_action_display()
        target_name = self.target.full_name if self.target else "Unknown"
        return f"{action} - {target_name} by {actor} at {self.timestamp.isoformat()}"
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', include('team.urls')),  # Connects your 'team' app routing table
]


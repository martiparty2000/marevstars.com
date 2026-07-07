from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

# Ако искаш началната страница да води към нещо конкретно:
urlpatterns = [
    path('', include('team.urls')), # Това ще зареди URL-ите от приложението ти 'team'
    path('admin/', admin.site.urls),
]


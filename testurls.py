"""
test URL Configuration for juntagrico_pg development
"""
from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'', include('juntagrico.urls')),
    path(r'', include('juntagrico_pg.urls')),
]

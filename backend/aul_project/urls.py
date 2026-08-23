"""
AUL URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from .views import home_view, feed_view, search_view, profile_view, profile_edit_view, services_view

urlpatterns = [
    path('', home_view, name='home'),
    path('feed/', feed_view, name='feed'),
    path('search/', search_view, name='search'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', profile_edit_view, name='profile_edit'),
    path('services/', services_view, name='services'),
    path('auth/', include('apps.users.urls')),
    path('', include('apps.users.urls')),
    path('admin/', admin.site.urls),
    path('notifications/', include('apps.notifications.urls')),
    path('trips/', include('apps.trips.urls')),
    path('ads/', include('apps.ads.urls')),
    path('directory/', include('apps.directory.urls')),
    path('api/weather/', include('apps.weather.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

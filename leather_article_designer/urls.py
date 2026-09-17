"""
URL configuration for leather_article_designer project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from articles.views import home_view, about_view
from accounts.views import login_view, register_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('about/', about_view, name='about'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


"""Main URL configuration for Team Task Manager."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.http import HttpResponse

urlpatterns = [
    path('admin/', admin.site.urls),

    # Health check for Railway deployment
    path('health/', lambda request: HttpResponse('OK', status=200), name='health'),

    # Root redirect to dashboard
    path('', lambda request: redirect('dashboard:index'), name='root'),

    # App URLs
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('projects/', include('apps.projects.urls', namespace='projects')),
    path('tasks/', include('apps.tasks.urls', namespace='tasks')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),

    # API
    path('api/v1/', include('apps.api.urls')),

    # Allauth
    path('auth/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

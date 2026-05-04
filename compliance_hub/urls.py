"""PNG Compliance Hub 2026 — Root URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    path('gst/', include('gst.urls')),
    path('swt/', include('swt.urls')),
    path('sbt/', include('sbt.urls')),
    path('reports/', include('reports.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

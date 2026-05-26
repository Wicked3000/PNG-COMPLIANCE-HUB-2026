"""PNG Compliance Hub 2026 - Root URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth.views import LogoutView

admin.site.site_header = 'PNG Compliance Hub Administration'
admin.site.site_title = 'PNG Compliance Hub'
admin.site.index_title = 'System Administration'

from core.views import impersonate_start, impersonate_stop

urlpatterns = [
    path('admin/logout/', LogoutView.as_view(next_page='/admin/login/')),
    path('admin/impersonate/stop/', impersonate_stop, name='impersonate_stop'),
    path('admin/impersonate/<int:user_id>/', impersonate_start, name='impersonate_start'),
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    path('gst/', include('gst.urls')),
    path('swt/', include('swt.urls')),
    path('sbt/', include('sbt.urls')),
    path('reports/',  include('reports.urls')),
    path('guide/',    include('tax_guide.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

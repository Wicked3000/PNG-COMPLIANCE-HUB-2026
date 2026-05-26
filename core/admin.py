from django.contrib import admin
from .models import SystemSettings

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'active_tax_year')
    
    def has_add_permission(self, request):
        # Prevent creating multiple instances
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse

admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Extends the default UserAdmin to add the 'Secretly Impersonate' button.
    """
    list_display = UserAdmin.list_display + ('impersonate_action',)
    
    def impersonate_action(self, obj):
        if not obj.is_superuser:
            url = reverse('impersonate_start', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" style="background-color: #721c24; color: white;">Secretly Impersonate</a>',
                url
            )
        return "N/A"
    impersonate_action.short_description = 'Ghost Mode'

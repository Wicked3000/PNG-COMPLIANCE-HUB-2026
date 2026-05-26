from core.models import SystemSettings

def global_settings(request):
    """Inject global system settings into all template contexts."""
    try:
        settings_obj = SystemSettings.load()
        tax_year = settings_obj.active_tax_year
    except Exception:
        # Fallback if DB isn't migrated yet
        tax_year = 2026

    return {
        'TAX_YEAR': str(tax_year),
        'APP_NAME': 'PNG Compliance Hub',
    }

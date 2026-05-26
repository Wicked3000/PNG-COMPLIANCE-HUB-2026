from django import template
from core.models import SystemErrorLog

register = template.Library()

@register.simple_tag
def get_unresolved_errors_count():
    return SystemErrorLog.objects.filter(is_resolved=False).count()

import json
from django import template
from django.db.models import Count
from accounts.models import BusinessProfile, PNG_PROVINCES
from core.models import SystemErrorLog

register = template.Library()

@register.simple_tag
def get_business_stats_json():
    # Get businesses grouped by province
    # Map the province choices to actual names for the chart labels
    province_dict = dict(PNG_PROVINCES)
    qs = BusinessProfile.objects.values('province').annotate(total=Count('id')).order_by('-total')
    
    labels = []
    data = []
    
    for row in qs:
        # e.g. "NCD" -> "National Capital District"
        labels.append(province_dict.get(row['province'], row['province']))
        data.append(row['total'])
        
    return json.dumps({
        "labels": labels,
        "data": data
    })

@register.simple_tag
def get_error_stats_json():
    # Group errors by resolved status
    unresolved = SystemErrorLog.objects.filter(is_resolved=False).count()
    resolved = SystemErrorLog.objects.filter(is_resolved=True).count()
    
    return json.dumps({
        "labels": ["Unresolved Errors", "Resolved Errors"],
        "data": [unresolved, resolved]
    })

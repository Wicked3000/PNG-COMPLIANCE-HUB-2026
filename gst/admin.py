"""GST Admin"""
from django.contrib import admin
from .models import DailyLedger, GSTReturn

@admin.register(DailyLedger)
class DailyLedgerAdmin(admin.ModelAdmin):
    list_display  = ['date', 'business', 'entry_type', 'description', 'amount_excl_gst', 'gst_amount']
    list_filter   = ['entry_type', 'date']
    search_fields = ['description', 'receipt_ref']

@admin.register(GSTReturn)
class GSTReturnAdmin(admin.ModelAdmin):
    list_display  = ['business', 'period_start', 'period_end', 'net_gst', 'status']
    list_filter   = ['status']

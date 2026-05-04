"""Accounts Admin"""
from django.contrib import admin
from .models import BusinessProfile

@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display  = ['business_name', 'tin', 'province', 'industry', 'gst_registered', 'sbt_eligible']
    search_fields = ['business_name', 'tin']
    list_filter   = ['province', 'industry', 'gst_registered']

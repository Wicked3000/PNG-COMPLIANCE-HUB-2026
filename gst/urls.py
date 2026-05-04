"""GST App — URL Configuration"""

from django.urls import path
from . import views

app_name = 'gst'

urlpatterns = [
    path('',             views.gst_dashboard,   name='dashboard'),
    path('ledger/',      views.ledger,           name='ledger'),
    path('ledger/add/',  views.add_entry,        name='add_entry'),
    path('returns/',     views.returns_list,     name='returns'),
    path('calculator/',  views.calculator,       name='calculator'),
]

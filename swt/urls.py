"""SWT App — URL Configuration"""

from django.urls import path
from . import views

app_name = 'swt'

urlpatterns = [
    path('',              views.swt_dashboard,  name='dashboard'),
    path('employees/',    views.employees,      name='employees'),
    path('payroll/',      views.payroll,         name='payroll'),
    path('calculator/',   views.calculator,     name='calculator'),
    path('returns/',      views.returns_list,   name='returns'),
]

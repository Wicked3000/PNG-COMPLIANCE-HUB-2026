"""Dashboard App — URL Configuration"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('',           views.dashboard,       name='home'),
    path('dashboard/', views.dashboard,       name='dashboard'),
    path('quick-log/', views.quick_log_sale,  name='quick_log_sale'),
]

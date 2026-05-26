"""SBT App - URL Configuration"""

from django.urls import path
from . import views

app_name = 'sbt'

urlpatterns = [
    path('',             views.sbt_dashboard,  name='dashboard'),
    path('calculator/',  views.calculator,     name='calculator'),
    path('declare/',     views.declare,        name='declare'),
]

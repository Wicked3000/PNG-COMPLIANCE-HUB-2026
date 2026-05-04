"""Reports App — URL Configuration"""

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('',                  views.reports_home,  name='home'),
    path('gst-return/<int:pk>/', views.gst_return_pdf, name='gst_return_pdf'),
    path('swt-return/<int:pk>/', views.swt_return_pdf, name='swt_return_pdf'),
    path('sbt-return/<int:pk>/', views.sbt_return_pdf, name='sbt_return_pdf'),
]

from django.urls import path
from . import views

app_name = 'tax_guide'

urlpatterns = [
    path('', views.guide_list, name='index'),
    path('<slug:slug>/', views.guide_detail, name='detail'),
]

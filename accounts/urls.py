"""Accounts App — URL Configuration"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/',    views.login_view,  name='login'),
    path('logout/',   views.logout_view, name='logout'),
    path('register/', views.register,    name='register'),
    path('setup/',    views.setup,       name='setup'),
    path('profile/',  views.profile,     name='profile'),

    # Biometrics (WebAuthn)
    path('biometric/register/options/', views.biometric_register_options, name='biometric_reg_options'),
    path('biometric/register/verify/',  views.biometric_register_verify,  name='biometric_reg_verify'),
    path('biometric/login/options/',    views.biometric_login_options,    name='biometric_login_options'),
    path('biometric/login/verify/',     views.biometric_login_verify,     name='biometric_login_verify'),
]

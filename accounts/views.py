"""Accounts App - Views"""

import json
import base64
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .models import BusinessProfile, UserCredential

# WebAuthn imports
try:
    import webauthn
    from webauthn.helpers.structs import (
        AuthenticatorSelectionCriteria,
        UserVerificationRequirement,
        AuthenticatorAttachment,
    )
    from webauthn import options_to_json, verify_registration_response, verify_authentication_response
    WEBAUTHN_AVAILABLE = True
except ImportError:
    WEBAUTHN_AVAILABLE = False


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            if user.is_staff:
                messages.error(request, 'Administrators must log in via the Admin Portal.')
                return render(request, 'accounts/login.html')
            login(request, user)
            return redirect(request.GET.get('next', 'dashboard:home'))
        messages.error(request, 'Invalid credentials. Please try again.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        username  = request.POST.get('username')
        email     = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            return redirect('accounts:setup')
    return render(request, 'accounts/register.html')


@login_required
def setup(request):
    """Business profile setup - shown after registration."""
    if hasattr(request.user, 'business'):
        return redirect('dashboard:home')
    if request.method == 'POST':
        BusinessProfile.objects.create(
            user=request.user,
            business_name=request.POST.get('business_name'),
            tin=request.POST.get('tin', ''),
            province=request.POST.get('province', 'NCD'),
            industry=request.POST.get('industry', 'RETAIL'),
            phone=request.POST.get('phone', ''),
            gst_registered=request.POST.get('gst_registered') == 'on',
            annual_turnover_estimate=request.POST.get('annual_turnover', 0) or 0,
        )
        messages.success(request, 'Business profile created! Welcome to PNG Compliance Hub.')
        return redirect('dashboard:home')
    from .models import PNG_PROVINCES, INDUSTRY_TYPES
    return render(request, 'accounts/setup.html', {
        'provinces': PNG_PROVINCES,
        'industries': INDUSTRY_TYPES,
    })


@login_required
def profile(request):
    try:
        business = request.user.business
    except BusinessProfile.DoesNotExist:
        return redirect('accounts:setup')
        
    if request.method == 'POST':
        business.role = request.POST.get('role', business.role)
        business.notify_method = request.POST.get('notify_method', business.notify_method)
        try:
            business.notify_days_before = int(request.POST.get('notify_days_before', business.notify_days_before))
        except ValueError:
            pass
        business.save()
        messages.success(request, 'System settings updated successfully.')
        return redirect('accounts:profile')
        
    credentials = UserCredential.objects.filter(user=request.user)
    return render(request, 'accounts/profile.html', {
        'business': business,
        'credentials': credentials,
        'webauthn_available': WEBAUTHN_AVAILABLE
    })

# ── WebAuthn Endpoints ───────────────────────────────────────────────────────

@login_required
def biometric_register_options(request):
    """Generate options for WebAuthn registration."""
    if not WEBAUTHN_AVAILABLE:
        return JsonResponse({'message': 'WebAuthn not installed'}, status=500)
    
    # Generate unique challenge and user ID
    raw_user_id = str(request.user.id).encode()
    user_id_b64 = base64.b64encode(raw_user_id).decode()
    raw_challenge = webauthn.helpers.generate_challenge()
    challenge_b64 = base64.b64encode(raw_challenge).decode()
    
    # Store challenge in session for verification
    request.session['webauthn_registration_challenge'] = challenge_b64
    
    options = webauthn.generate_registration_options(
        rp_id=request.get_host().split(':')[0],
        rp_name='PNG Compliance Hub',
        user_id=raw_user_id,
        user_name=request.user.username,
        challenge=raw_challenge,
    )
    # The helper ensures byte fields are correctly converted for JSON
    return JsonResponse(json.loads(options_to_json(options)))


@csrf_exempt
@login_required
def biometric_register_verify(request):
    """Verify WebAuthn registration response."""
    if request.method != 'POST':
        return JsonResponse({'message': 'POST required'}, status=405)
    
    body = json.loads(request.body)
    challenge = request.session.get('webauthn_registration_challenge')
    
    try:
        expected_challenge = base64.b64decode(challenge)
        verification = verify_registration_response(
            credential=body,
            expected_challenge=expected_challenge,
            expected_origin=f"http://{request.get_host()}",
            expected_rp_id=request.get_host().split(':')[0],
        )
        
        # Save credential to DB
        UserCredential.objects.create(
            user=request.user,
            credential_id=verification.credential_id,
            public_key=verification.public_key,
            sign_count=verification.sign_count,
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)


def biometric_login_options(request):
    """Generate options for WebAuthn authentication."""
    # Simulation: We'll assume the user is trying to log in
    # In a real app, you'd find the user by username or credential ID
    raw_challenge = webauthn.helpers.generate_challenge()
    challenge_b64 = base64.b64encode(raw_challenge).decode()
    request.session['webauthn_login_challenge'] = challenge_b64
    
    options = webauthn.generate_authentication_options(
        rp_id=request.get_host().split(':')[0],
        challenge=raw_challenge,
    )
    return JsonResponse(json.loads(options_to_json(options)))


@csrf_exempt
def biometric_login_verify(request):
    """Verify WebAuthn authentication response."""
    body = json.loads(request.body)
    challenge = request.session.get('webauthn_login_challenge')
    
    # Find credential in DB
    try:
        cred_record = UserCredential.objects.get(credential_id=body['id'])
        user = cred_record.user
        expected_challenge = base64.b64decode(challenge)
        
        verification = verify_authentication_response(
            credential=body,
            expected_challenge=expected_challenge,
            expected_origin=f"http://{request.get_host()}",
            expected_rp_id=request.get_host().split(':')[0],
            credential_public_key=cred_record.public_key,
            credential_current_sign_count=cred_record.sign_count,
        )
        
        # Update sign count
        cred_record.sign_count = verification.new_sign_count
        cred_record.save()
        
        # Log user in
        login(request, user)
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)

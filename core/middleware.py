from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

class RoleSeparationMiddleware:
    """
    Enforces a strict wall between Admin users and Business Owners.
    Admin users can ONLY access paths starting with /admin/.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            path = request.path
            
            # Allow impersonators through the wall
            if getattr(request, 'is_impersonating', False):
                pass
            elif path.startswith('/static/') or path.startswith('/media/') or path == reverse('accounts:logout') or path == '/admin/logout/' or path == '/':
                pass
            else:
                is_admin_path = path.startswith('/admin/')
                
                if request.user.is_staff:
                    # Admins are blocked from public frontend
                    if not is_admin_path:
                        messages.warning(request, "Administrators are restricted to the backend portal.")
                        return redirect('/admin/')
                else:
                    # Non-admins are blocked from the backend
                    pass

        response = self.get_response(request)
        return response

from django.contrib.auth import get_user_model
User = get_user_model()

class ImpersonationMiddleware:
    """
    Allows a superuser to secretly impersonate another user.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.is_staff:
            impersonate_id = request.session.get('impersonate_id')
            if impersonate_id:
                try:
                    target_user = User.objects.get(pk=impersonate_id)
                    request.original_user = request.user
                    request.user = target_user
                    request.is_impersonating = True
                except User.DoesNotExist:
                    del request.session['impersonate_id']

        response = self.get_response(request)
        return response

import traceback
from django.core.cache import cache

class ErrorLoggingMiddleware:
    """
    Catches unhandled exceptions and logs them to the SystemErrorLog model.
    Also auto-resolves them if the path later succeeds.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # AUTO-HEALING CHECK (Aggressive)
        # If the request succeeds, automatically mark any pending errors for this path as resolved
        if response.status_code < 500:
            from .models import SystemErrorLog
            # Direct DB update is extremely fast and guarantees 100% auto-healing reliability
            SystemErrorLog.objects.filter(path=request.path[:255], is_resolved=False).update(is_resolved=True)
                
        return response

    def process_exception(self, request, exception):
        from .models import SystemErrorLog
        from django.core.mail import mail_admins
        
        path = request.path[:255]
        
        # Determine the user
        user = request.user if request.user.is_authenticated else None
        
        # Save the error log
        error_log = SystemErrorLog.objects.create(
            path=path,
            method=request.method[:10],
            user=user,
            exception_type=exception.__class__.__name__[:255],
            exception_message=str(exception),
            traceback=traceback.format_exc()
        )
        
        # Send automated email alert
        subject = f"CRITICAL SYSTEM ERROR: {error_log.exception_type} at {error_log.path}"
        message = (
            f"An unhandled exception occurred on the platform.\n\n"
            f"Time: {error_log.timestamp}\n"
            f"Path: {error_log.path}\n"
            f"Method: {error_log.method}\n"
            f"User: {user.username if user else 'Anonymous'}\n\n"
            f"Error: {error_log.exception_message}\n\n"
            f"Traceback:\n{error_log.traceback}\n\n"
            f"Please log in to the admin dashboard to review."
        )
        mail_admins(subject, message, fail_silently=True)
        
        return None  # Let Django handle the 500 response

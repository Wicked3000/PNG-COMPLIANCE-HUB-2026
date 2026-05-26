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

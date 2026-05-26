from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

User = get_user_model()

@staff_member_required
def impersonate_start(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    if target_user.is_superuser:
        messages.error(request, "You cannot impersonate another superuser.")
        return redirect('admin:auth_user_changelist')
        
    request.session['impersonate_id'] = target_user.id
    messages.success(request, f"You are now secretly impersonating {target_user.username}.")
    return redirect('dashboard:home')

@staff_member_required
def impersonate_stop(request):
    if 'impersonate_id' in request.session:
        del request.session['impersonate_id']
        messages.success(request, "Impersonation session ended. Welcome back.")
    return redirect('admin:auth_user_changelist')

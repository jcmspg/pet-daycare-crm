from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


@login_required
def smart_redirect(request):
    """
    Redirect authenticated user to appropriate dashboard based on role hierarchy:
    1. Admin/Superuser (joao) → Django admin panel (service owner)
    2. Business Manager → Staff dashboard with full permissions
    3. Business Staff → Staff dashboard with limited permissions
    4. Tutor → Tutor dashboard
    """
    user = request.user
    
    # PRIORITY 1: Check if user is superuser or admin (service owner)
    if user.is_superuser:
        return redirect('admin:index')
    
    # PRIORITY 2: Check if user is business staff (manager or staff role)
    if hasattr(user, 'staff_profile') and user.staff_profile:
        return redirect('staff:dashboard')
    
    # PRIORITY 3: Check if user is a tutor (pet parent)
    if hasattr(user, 'tutor_profile') and user.tutor_profile:
        return redirect('tutor:dashboard')
    
    # Default fallback (no role assigned)

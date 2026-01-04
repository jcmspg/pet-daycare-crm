from django.shortcuts import redirect
from django.urls import reverse

class AdminAccessMiddleware:
    """
    Middleware to restrict admin panel access to superusers only.
    Non-superuser staff and tutors will be redirected to their dashboards.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is trying to access /admin/
        if request.path.startswith('/admin/'):
            # Allow if superuser
            if not request.user.is_superuser:
                # Redirect based on user type
                if request.user.is_authenticated:
                    # Check if they're staff or tutor
                    if hasattr(request.user, 'staff_profile'):
                        return redirect('staff:dashboard')
                    elif hasattr(request.user, 'tutor_profile'):
                        return redirect('tutor:dashboard')
                    else:
                        # No profile, go to home
                        return redirect('home:index')
                else:
                    return redirect('account_login')
        
        response = self.get_response(request)
        return response

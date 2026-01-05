from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from .models import Invitation, BusinessInquiry


def error_page(request, error_title="Error", error_message="Something went wrong", show_details=False, error_details=""):
    """Generic error page"""
    context = {
        'error_title': error_title,
        'error_message': error_message,
        'show_details': show_details and not request.user.is_authenticated,  # Only show details to unauthenticated users for security
        'error_details': error_details,
    }
    return render(request, 'error.html', context, status=400)


def permission_denied(request, exception=None):
    """Permission denied error page"""
    return render(request, 'error.html', {
        'error_title': 'Access Denied',
        'error_message': 'You do not have permission to access this page.',
        'show_details': False,
    }, status=403)


def not_found(request, exception=None):
    """Not found error page"""
    return render(request, 'error.html', {
        'error_title': 'Page Not Found',
        'error_message': 'The page you are looking for does not exist.',
        'show_details': False,
    }, status=404)


def server_error(request):
    """Server error page"""
    return render(request, 'error.html', {
        'error_title': 'Server Error',
        'error_message': 'An unexpected error occurred. Our team has been notified.',
        'show_details': False,
    }, status=500)


def home(request):
    """Landing page"""
    return render(request, 'home/index.html')


def tutor_entry(request):
    """Tutor login/entry page"""
    return render(request, 'home/tutor_entry.html')


def business_entry(request):
    """Business login/entry page"""
    return render(request, 'home/business_entry.html')


def for_pet_parents(request):
    """Landing page for pet parents with share functionality"""
    return render(request, 'home/for_pet_parents.html')


def for_businesses(request):
    """Landing page for businesses with inquiry form"""
    if request.method == 'POST':
        # Handle inquiry form submission
        inquiry = BusinessInquiry.objects.create(
            business_name=request.POST.get('business_name', ''),
            contact_name=request.POST.get('contact_name', ''),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            num_locations=request.POST.get('num_locations') or None,
            message=request.POST.get('message', ''),
        )
        
        # Return JSON response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Inquiry submitted successfully'})
        
        # Redirect with success message for regular form submissions
        messages.success(request, 'Thank you! We will contact you within 24 hours.')
        return redirect('home:for_businesses')
    
    return render(request, 'home/for_businesses.html')


def accept_invitation(request, invitation_id):
    """Accept an invitation and create account"""
    invitation = get_object_or_404(Invitation, id=invitation_id)
    
    if not invitation.is_valid:
        messages.error(request, 'This invitation has already been used or expired.')
        return redirect('home:index')
    
    if request.method == 'POST':
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        
        if not password or not password_confirm:
            messages.error(request, 'Please enter a password.')
            return render(request, 'home/accept_invitation.html', {'invitation': invitation})
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'home/accept_invitation.html', {'invitation': invitation})
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'home/accept_invitation.html', {'invitation': invitation})
        
        # Create user
        from django.contrib.auth.models import User
        user = User.objects.create_user(
            username=invitation.email,
            email=invitation.email,
            password=password
        )
        
        # Mark invitation as used
        invitation.used_at = timezone.now()
        invitation.used_by = user
        invitation.save()
        
        # Create Tutor or Staff profile based on role
        if invitation.role == 'tutor':
            from pets.models import Tutor
            Tutor.objects.create(
                user=user,
                email=invitation.email,
                business=invitation.business
            )
            messages.success(request, 'Account created! You can now sign in and add your pets.')
        elif invitation.role == 'staff':
            from pets.models import Staff
            Staff.objects.create(
                user=user,
                business=invitation.business,
                role='staff'
            )
            messages.success(request, 'Account created! You can now sign in.')
        
        return redirect('account_login')
    
    return render(request, 'home/accept_invitation.html', {'invitation': invitation})

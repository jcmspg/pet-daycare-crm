from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
import json
from pets.models import Business, Pet
from reservations.models import CheckIn, ServiceBooking
from tutor.models import Woof, WoofLog, GlobalWoof
from django.shortcuts import get_object_or_404
from pets.models import TrainingProgress

def staff_login(request):
    if request.method == 'POST':
        business_code = request.POST.get('business_code', '').strip()
        
        if not business_code:
            return render(request, 'staff/login.html', {
                'error': 'Please enter a business code.'
            })
        
        # Try to find business by name (case-insensitive)
        business = Business.objects.filter(name__icontains=business_code).first()
        
        if not business:
            return render(request, 'staff/login.html', {
                'business_code': business_code,
                'error': 'Business not found. Please check your code and try again.'
            })
        
        # Store business ID in session
        request.session['business_id'] = business.id
        messages.success(request, f'Welcome to {business.name}!')
        return redirect('staff:dashboard')
    
    return render(request, 'staff/login.html')

def staff_logout(request):
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('staff:login')

@login_required
def dashboard(request):
    # Get business from session
    business_id = request.session.get('business_id')
    
    if not business_id:
        return redirect('staff:login')
    
    try:
        business = Business.objects.get(id=business_id)
    except Business.DoesNotExist:
        messages.error(request, 'Business not found. Please log in again.')
        return redirect('staff:login')
    
    pets = Pet.objects.filter(business=business)
    pet_checkins = {pet.id: CheckIn.objects.filter(pet=pet).first() for pet in pets}
    # Recent public community woofs for staff feed preview (optional)
    recent_woofs = Woof.objects.filter(parent_woof__isnull=True, visibility='public').order_by('-created_at')[:10]
    
    # ADD STATS
    in_house_count = sum(1 for checkin in pet_checkins.values() if checkin and checkin.is_present)
    occupancy_pct = (in_house_count / len(pets) * 100) if pets else 0
    
    if request.method == 'POST':
        action = request.POST.get('action')
        pet_id = request.POST.get('pet_id')
        pet = None
        checkin = None
        created = False
        if action in ['checkin', 'checkout', 'woof']:
            if not pet_id:
                messages.error(request, 'Pet ID is required for this action.')
                return redirect('staff:dashboard')
            try:
                pet = Pet.objects.get(id=pet_id)
            except Pet.DoesNotExist:
                messages.error(request, 'Pet not found.')
                return redirect('staff:dashboard')
            checkin, created = CheckIn.objects.get_or_create(pet=pet)
        
        if action == 'checkin':
            checkin.is_present = True
            checkin.checkin_time = timezone.now()
            checkin.checkout_time = None
            checkin.save()
            
            if created:
                try:
                    woof = Woof.objects.create(
                        pet=pet,
                        message=f"🐕 {pet.name} checked in at {timezone.now().time()}! Happy tail wagging! 🐶",
                        staff=request.user
                    )
                    WoofLog.objects.create(
                        woof=woof,
                        action="created",
                        user=request.user,
                        ip_address=request.META.get('REMOTE_ADDR')
                    )
                except Exception:
                    pass
            
            messages.success(request, f"✅ {pet.name} checked IN at {timezone.now().strftime('%H:%M')}")
        elif action == 'checkout':
            checkin.is_present = False
            checkin.checkout_time = timezone.now()
            checkin.save()
            messages.success(request, f"❌ {pet.name} checked OUT at {timezone.now().strftime('%H:%M')}")
        elif action == 'woof':
            message = request.POST.get('woof_message', '').strip()
            attachment = request.FILES.get('woof_attachment')
            visibility = request.POST.get('visibility', 'public')
            if message:
                woof = Woof.objects.create(
                    pet=pet,
                    message=message,
                    staff=request.user,
                    attachment=attachment,
                    visibility=visibility
                )
                WoofLog.objects.create(
                    woof=woof,
                    action="created",
                    user=request.user,
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                messages.success(request, f'Woof added for {pet.name}!')
        elif action == 'global_woof':
            message = request.POST.get('global_message', '').strip()
            attachment = request.FILES.get('global_attachment')
            if message or attachment:
                GlobalWoof.objects.create(message=message, staff=request.user, attachment=attachment)
                messages.success(request, 'Global woof sent to all tutors!')
        elif action == 'confirm_booking':
            booking_id = request.POST.get('booking_id')
            try:
                booking = ServiceBooking.objects.get(id=booking_id)
                booking.confirm()
                messages.success(request, f'✅ Confirmed booking for {booking.pet.name} - {booking.slot.service.type} on {booking.slot.date}')
            except ServiceBooking.DoesNotExist:
                messages.error(request, 'Booking not found.')
        elif action == 'reject_booking':
            booking_id = request.POST.get('booking_id')
            try:
                booking = ServiceBooking.objects.get(id=booking_id)
                booking.cancel()
                messages.success(request, f'❌ Rejected booking for {booking.pet.name} - {booking.slot.service.type}')
            except ServiceBooking.DoesNotExist:
                messages.error(request, 'Booking not found.')
        
        return redirect('staff:dashboard')
    
    # Get pending service booking requests
    pending_bookings = ServiceBooking.objects.filter(status='pending').select_related('pet', 'tutor', 'slot__service').order_by('-requested_at')
    
    # Generate booking data for mini calendars (next 15 days)
    pet_bookings_json = {}
    today = timezone.now().date()
    
    for pet in pets:
        pet_bookings = ServiceBooking.objects.filter(
            pet=pet,
            status__in=['pending', 'confirmed']
        ).select_related('slot').order_by('slot__date')
        
        pet_bookings_by_date = {}
        for booking in pet_bookings:
            date_str = booking.slot.date.isoformat()
            if date_str not in pet_bookings_by_date:
                pet_bookings_by_date[date_str] = []
            
            pet_bookings_by_date[date_str].append({
                'id': booking.id,
                'status': booking.status,
                'service': booking.slot.service.type,
                'time': booking.slot.start_time.strftime('%H:%M'),
            })
        
        pet_bookings_json[pet.id] = pet_bookings_by_date
    
    return render(request, 'staff/dashboard_new.html', {
        'business': business,
        'pets': pets,
        'pet_checkins': pet_checkins,
        'in_house_count': in_house_count,
        'occupancy_pct': occupancy_pct,
        'recent_woofs': recent_woofs,
        'pending_bookings': pending_bookings,
        'pet_bookings_json': json.dumps(pet_bookings_json),
    })


@login_required
def feed(request):
    # Get business from session
    business_id = request.session.get('business_id')
    
    if not business_id:
        return redirect('staff:login')
    
    try:
        business = Business.objects.get(id=business_id)
    except Business.DoesNotExist:
        messages.error(request, 'Business not found. Please log in again.')
        return redirect('staff:login')
    
    pets = Pet.objects.filter(business=business).order_by('name')
    pet_checkins = {pet.id: CheckIn.objects.filter(pet=pet).first() for pet in pets}

    # Unified feed: pet woofs (all, top-level) + global woofs
    pet_woofs = Woof.objects.filter(parent_woof__isnull=True).select_related('pet', 'staff').order_by('-created_at')
    global_woofs = GlobalWoof.objects.select_related('staff').order_by('-created_at')

    # Normalize to unified list with label and type for rendering
    feed_items = []
    for gw in global_woofs:
        feed_items.append({
            'type': 'global',
            'label': 'BUSINESS',
            'created_at': gw.created_at,
            'author': gw.staff,
            'message': gw.message,
            'attachment': gw.attachment,
            'obj': gw,
        })
    for w in pet_woofs:
        feed_items.append({
            'type': 'pet',
            'label': w.pet.name if w.pet else 'PET',
            'created_at': w.created_at,
            'author': w.staff or w.tutor,
            'message': w.message,
            'attachment': w.attachment,
            'obj': w,
        })

    feed_items.sort(key=lambda x: x['created_at'], reverse=True)

    # Pagination
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    page_size = 20
    start = (page - 1) * page_size
    end = start + page_size
    total = len(feed_items)
    page_items = feed_items[start:end]

    # JSON for auto-refresh
    if request.GET.get('format') == 'json':
        since = request.GET.get('since')
        new_items = []
        from django.utils.dateparse import parse_datetime
        since_dt = parse_datetime(since) if since else None
        for item in feed_items:
            if since_dt and item['created_at'] <= since_dt:
                break
            new_items.append({
                'type': item['type'],
                'label': item['label'],
                'created_at': item['created_at'].isoformat(),
                'author': getattr(item['author'], 'first_name', getattr(item['author'], 'name', '')) if item['author'] else '',
                'message': item['message'] or '',
                'attachment_url': item['attachment'].url if item['attachment'] else '',
            })
        from django.http import JsonResponse
        return JsonResponse({'items': new_items})

    # POST handling: allow actions (checkin/checkout/woof/global_woof) from the same page
    if request.method == 'POST':
        action = request.POST.get('action')
        pet_id = request.POST.get('pet_id')
        pet = None
        checkin = None
        created = False
        if action in ['checkin', 'checkout', 'woof']:
            if not pet_id:
                messages.error(request, 'Pet ID is required for this action.')
                return redirect('staff:feed')
            try:
                pet = Pet.objects.get(id=pet_id)
            except Pet.DoesNotExist:
                messages.error(request, 'Pet not found.')
                return redirect('staff:feed')
            checkin, created = CheckIn.objects.get_or_create(pet=pet)

        if action == 'checkin':
            checkin.is_present = True
            checkin.checkin_time = timezone.now()
            checkin.checkout_time = None
            checkin.save()
            messages.success(request, f"✅ {pet.name} checked IN at {timezone.now().strftime('%H:%M')}")
        elif action == 'checkout':
            checkin.is_present = False
            checkin.checkout_time = timezone.now()
            checkin.save()
            messages.success(request, f"❌ {pet.name} checked OUT at {timezone.now().strftime('%H:%M')}")
        elif action == 'woof':
            message = request.POST.get('woof_message', '').strip()
            attachment = request.FILES.get('woof_attachment')
            visibility = request.POST.get('visibility', 'private')
            if message or attachment:
                woof = Woof.objects.create(
                    pet=pet,
                    message=message,
                    staff=request.user,
                    attachment=attachment,
                    visibility=visibility
                )
                WoofLog.objects.create(
                    woof=woof,
                    action="created",
                    user=request.user,
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                messages.success(request, f'Woof added for {pet.name}!')
        elif action == 'global_woof':
            message = request.POST.get('global_message', '').strip()
            attachment = request.FILES.get('global_attachment')
            if message or attachment:
                GlobalWoof.objects.create(message=message, staff=request.user, attachment=attachment)
                messages.success(request, 'Global woof sent to all tutors!')
        elif action == 'woof_reply_staff':
            parent_id = request.POST.get('parent_woof_id')
            message = request.POST.get('woof_message', '').strip()
            attachment = request.FILES.get('woof_attachment')
            try:
                parent = Woof.objects.get(id=parent_id)
            except Woof.DoesNotExist:
                messages.error(request, 'Original woof not found.')
                return redirect('staff:feed')
            if not message and not attachment:
                messages.error(request, 'Reply cannot be empty.')
                return redirect('staff:feed')
            Woof.objects.create(
                pet=parent.pet,
                message=message or '',
                staff=request.user,
                parent_woof=parent,
                attachment=attachment
            )
            messages.success(request, 'Reply sent!')

        return redirect('staff:feed')

    return render(request, 'staff/feed.html', {
        'business': business,
        'pets': pets,
        'pet_checkins': pet_checkins,
        'feed_items': page_items,
        'page': page,
        'has_next': end < total,
        'next_page': page + 1,
    })

@login_required
def pet_sheet(request, pet_id):
    # Get business from session
    business_id = request.session.get('business_id')
    
    if not business_id:
        return redirect('staff:login')
    
    try:
        business = Business.objects.get(id=business_id)
    except Business.DoesNotExist:
        messages.error(request, 'Business not found. Please log in again.')
        return redirect('staff:login')
    
    pet = get_object_or_404(Pet, id=pet_id, business=business)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_training':
            title = request.POST.get('title', '').strip()
            notes = request.POST.get('notes', '').strip()
            try:
                progress = int(request.POST.get('progress', '0'))
            except ValueError:
                progress = 0
            progress = max(0, min(100, progress))
            if title:
                TrainingProgress.objects.create(pet=pet, title=title, notes=notes, progress=progress)
                from django.contrib import messages
                messages.success(request, 'Training entry added!')
            else:
                from django.contrib import messages
                messages.error(request, 'Title is required for training entry.')
        elif action == 'update_pet':
            # Update pet metadata from form
            pet.name = request.POST.get('name', pet.name).strip() or pet.name
            pet.species = request.POST.get('species', '')
            pet.breed = request.POST.get('breed', '')
            pet.sex = request.POST.get('sex', pet.sex)
            pet.neutered = request.POST.get('neutered') == 'on'
            pet.allergies = request.POST.get('allergies', '')
            pet.address = request.POST.get('address', '')
            pet.chip_number = request.POST.get('chip_number', '')
            pet.notes = request.POST.get('notes', pet.notes)
            # Handle photo upload
            photo = request.FILES.get('photo')
            if photo:
                pet.photo = photo
            bday = request.POST.get('birthday')
            if bday:
                try:
                    from datetime import datetime
                    pet.birthday = datetime.strptime(bday, '%Y-%m-%d').date()
                except ValueError:
                    from django.contrib import messages
                    messages.warning(request, 'Invalid birthday format. Use YYYY-MM-DD.')
            pet.save()
            from django.contrib import messages
            messages.success(request, 'Pet information updated!')
        return redirect('staff:pet_sheet', pet_id=pet.id)

    training_entries = pet.training_entries.all()[:20]
    return render(request, 'staff/pet_sheet.html', {
        'pet': pet,
        'training_entries': training_entries,
    })

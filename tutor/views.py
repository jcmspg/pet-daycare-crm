from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.core import serializers
import json
from pets.models import Tutor, Pet, TrainingProgress
from reservations.models import CheckIn, TutorSchedule, Service, ServiceSlot, ServiceBooking
from .models import Woof, GlobalWoof
from pets.models import Business
from datetime import datetime, timedelta

def tutor_dashboard(request):
    phone = request.GET.get('phone', '').strip()
    
    if not phone:
        return render(request, 'tutor/login.html')
    
    tutor = Tutor.objects.filter(phone__icontains=phone).first()
    
    if not tutor:
        return render(request, 'tutor/login.html', {
            'phone': phone,
            'error': 'Tutor not found. Try again.'
        })
    
    pets = tutor.pets.all()
    business = Business.objects.first()
    
    # MATCH STAFF LOGIC - create pet_checkins dict
    pet_checkins = {}
    for pet in pets:
        checkins = CheckIn.objects.filter(pet=pet).order_by('-checkin_time')
        pet_checkins[pet.id] = checkins.first() if checkins.exists() else None
    
    # Build unified feed: pet woofs + global woofs, newest first
    # Public woofs + private woofs for this tutor's pets
    pet_woofs = Woof.objects.filter(pet__in=pets, parent_woof__isnull=True).filter(
        Q(visibility='public') | Q(visibility='private')
    )
    global_woofs = GlobalWoof.objects.all()
    feed = []
    for w in pet_woofs:
        feed.append({
            'kind': 'pet',
            'label': w.pet.name,
            'created_at': w.created_at,
            'message': w.message,
            'attachment': w.attachment,
            'author_staff': w.staff,
            'author_tutor': w.tutor,
            'woof': w,
        })
    for gw in global_woofs:
        feed.append({
            'kind': 'business',
            'label': 'BUSINESS',
            'created_at': gw.created_at,
            'message': gw.message,
            'attachment': gw.attachment,
            'author_staff': gw.staff,
            'author_tutor': None,
            'global': gw,
            'woof': None,
        })
    feed.sort(key=lambda x: x['created_at'], reverse=True)

    # Tutor replies
    if request.method == 'POST' and request.POST.get('action') == 'woof_reply_tutor':
        parent_id = request.POST.get('parent_woof_id')
        message = request.POST.get('woof_message', '').strip()
        attachment = request.FILES.get('woof_attachment')
        try:
            parent = Woof.objects.get(id=parent_id)
        except Woof.DoesNotExist:
            messages.error(request, 'Original woof not found.')
            return redirect(request.path + f'?phone={phone}')
        if not message and not attachment:
            messages.error(request, 'Reply cannot be empty.')
            return redirect(request.path + f'?phone={phone}')
        Woof.objects.create(
            pet=parent.pet,
            message=message or '',
            tutor=tutor,
            parent_woof=parent,
            attachment=attachment
        )
        messages.success(request, 'Reply sent!')
        return redirect(request.path + f'?phone={phone}')
    
    # Tutor replies to global woofs
    if request.method == 'POST' and request.POST.get('action') == 'woof_reply_global':
        global_id = request.POST.get('global_woof_id')
        message = request.POST.get('woof_message', '').strip()
        attachment = request.FILES.get('woof_attachment')
        try:
            global_woof = GlobalWoof.objects.get(id=global_id)
        except GlobalWoof.DoesNotExist:
            messages.error(request, 'Global woof not found.')
            return redirect(request.path + f'?phone={phone}')
        if not message and not attachment:
            messages.error(request, 'Reply cannot be empty.')
            return redirect(request.path + f'?phone={phone}')
        # For global replies, use the first pet or None (if we make pet optional)
        # For now, use first pet from tutor's pets
        pet = tutor.pets.first() if tutor.pets.exists() else None
        Woof.objects.create(
            pet=pet,
            message=message or '',
            tutor=tutor,
            parent_woof=None,
            attachment=attachment,
        )
        messages.success(request, 'Reply sent!')
        return redirect(request.path + f'?phone={phone}')
    
    # Handle service booking requests
    if request.method == 'POST' and request.POST.get('action') == 'book_service':
        selected_slots_json = request.POST.get('selected_slots', '[]')
        pet_id = request.POST.get('pet_id')
        notes = request.POST.get('booking_notes', '').strip()
        service_type = request.POST.get('selected_service_type', '')
        
        try:
            # Parse the JSON array of slot IDs
            slot_ids = json.loads(selected_slots_json)
            if not slot_ids:
                messages.error(request, 'Please select at least one time slot.')
                return redirect(request.path + f'?phone={phone}')
            
            pet = Pet.objects.get(id=pet_id)
            
            if pet not in pets:
                messages.error(request, 'Pet not found in your pets.')
                return redirect(request.path + f'?phone={phone}')
            
            booked_count = 0
            failed_slots = []
            
            for slot_id in slot_ids:
                try:
                    slot = ServiceSlot.objects.get(id=slot_id)
                    
                    if slot.is_fully_booked():
                        failed_slots.append(f'{slot.start_time} - {slot.end_time}')
                        continue
                    
                    # Check if already booked
                    existing = ServiceBooking.objects.filter(slot=slot, pet=pet, status__in=['pending', 'confirmed']).exists()
                    if existing:
                        failed_slots.append(f'{slot.start_time} - {slot.end_time}')
                        continue
                    
                    ServiceBooking.objects.create(
                        slot=slot,
                        pet=pet,
                        tutor=tutor,
                        notes=notes,
                        status='pending'
                    )
                    booked_count += 1
                except ServiceSlot.DoesNotExist:
                    failed_slots.append('Unknown slot')
            
            if booked_count > 0:
                msg = f'✅ Booking request sent for {pet.name} ({booked_count} slot{"s" if booked_count != 1 else ""})! Staff will confirm shortly.'
                messages.success(request, msg)
            
            if failed_slots:
                msg = f'⚠️ Could not book: {", ".join(failed_slots)} (already booked or full)'
                messages.warning(request, msg)
            
            return redirect(request.path + f'?phone={phone}')
        except (Pet.DoesNotExist, json.JSONDecodeError):
            messages.error(request, 'Invalid request data.')
            return redirect(request.path + f'?phone={phone}')
    
    # Get available service slots for next 30 days
    today = datetime.now().date()
    next_30_days = [today + timedelta(days=i) for i in range(30)]
    
    # Get all available service slots
    available_slots = ServiceSlot.objects.filter(
        date__gte=today,
        date__lte=today + timedelta(days=29),
        is_available=True
    ).select_related('service').order_by('date', 'start_time')
    
    # Group slots by date
    slots_by_date = {}
    for slot in available_slots:
        if slot.date not in slots_by_date:
            slots_by_date[slot.date] = []
        slots_by_date[slot.date].append(slot)
    
    # Get tutor's existing bookings
    tutor_bookings = ServiceBooking.objects.filter(
        tutor=tutor,
        slot__date__gte=today
    ).select_related('slot', 'pet')
    
    bookings_by_slot = {b.slot_id: b for b in tutor_bookings}
    
    # Convert slots to JSON for JavaScript calendar
    slots_json = {}
    for date_obj, slots_list in slots_by_date.items():
        date_str = date_obj.isoformat()
        slots_json[date_str] = []
        for slot in slots_list:
            slots_json[date_str].append({
                'id': slot.id,
                'service_type': slot.service.type,
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
                'available_spots': slot.available_spots(),
                'is_fully_booked': slot.is_fully_booked(),
            })
    
    # Convert bookings to JSON for JavaScript (organized by date with status)
    bookings_by_date_json = {}
    for booking in tutor_bookings:
        date_str = booking.slot.date.isoformat()
        if date_str not in bookings_by_date_json:
            bookings_by_date_json[date_str] = []
        bookings_by_date_json[date_str].append({
            'id': booking.id,
            'slot_id': booking.slot_id,
            'status': booking.status,
            'pet_name': booking.pet.name,
            'service_type': booking.slot.service.type,
            'start_time': booking.slot.start_time.strftime('%H:%M'),
            'end_time': booking.slot.end_time.strftime('%H:%M'),
            'requested_at': booking.requested_at.isoformat(),
        })
    
    slots_json_str = json.dumps(slots_json)
    bookings_json_str = json.dumps(bookings_by_date_json)
    
    return render(request, 'tutor/dashboard_new.html', {
        'tutor': tutor,
        'pets': pets,
        'feed': feed,
        'pet_checkins': pet_checkins,
        'business': business,
        'slots_by_date': slots_by_date,
        'next_30_days': next_30_days,
        'today': today,
        'bookings_by_slot': bookings_by_slot,
        'slots_json': slots_json_str,
        'bookings_json': bookings_json_str,
    })

def tutor_profile(request):
    phone = request.GET.get('phone', '').strip()
    
    if not phone:
        return redirect('tutor:dashboard')
    
    tutor = Tutor.objects.filter(phone__icontains=phone).first()
    
    if not tutor:
        messages.error(request, 'Tutor not found.')
        return redirect('tutor:dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profile':
            tutor.name = request.POST.get('name', tutor.name).strip() or tutor.name
            tutor.email = request.POST.get('email', '')
            tutor.phone = request.POST.get('phone', tutor.phone)
            tutor.address = request.POST.get('address', '')
            tutor.notes = request.POST.get('notes', '')
            tutor.save()
            messages.success(request, 'Profile updated successfully!')
        return redirect(f'/tutor/profile/?phone={phone}')
    
    return render(request, 'tutor/profile.html', {
        'tutor': tutor,
    })

def tutor_pet_sheet(request, pet_id):
    phone = request.GET.get('phone', '').strip()
    
    if not phone:
        return redirect('tutor:dashboard')
    
    tutor = Tutor.objects.filter(phone__icontains=phone).first()
    
    if not tutor:
        messages.error(request, 'Tutor not found.')
        return redirect('tutor:dashboard')
    
    pet = get_object_or_404(Pet, id=pet_id)
    
    # Verify tutor owns this pet
    if pet not in tutor.pets.all():
        messages.error(request, 'You do not have access to this pet.')
        return redirect(f'/tutor/?phone={phone}')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_pet':
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
                    pet.birthday = datetime.strptime(bday, '%Y-%m-%d').date()
                except ValueError:
                    messages.warning(request, 'Invalid birthday format. Use YYYY-MM-DD.')
            pet.save()
            messages.success(request, 'Pet information updated!')
        return redirect(f'/tutor/pet/{pet.id}/?phone={phone}')
    
    training_entries = pet.training_entries.all()[:20]
    
    return render(request, 'tutor/pet_sheet.html', {
        'tutor': tutor,
        'pet': pet,
        'training_entries': training_entries,
    })

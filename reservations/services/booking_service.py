"""
Booking service - Centralized booking business logic
"""
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from reservations.models import ServiceBooking, ServiceSlot


class BookingService:
    """Service class for booking operations"""
    
    @staticmethod
    @transaction.atomic
    def confirm_booking(booking, staff_user):
        """
        Confirm a booking request.
        
        Args:
            booking: ServiceBooking instance
            staff_user: User who is confirming the booking
            
        Returns:
            ServiceBooking: Confirmed booking instance
            
        Raises:
            ValidationError: If booking cannot be confirmed
        """
        # Validate booking status
        if booking.status != 'pending':
            raise ValidationError(f'Only pending bookings can be confirmed. Current status: {booking.status}')
        
        # Validate slot availability
        if booking.slot.is_fully_booked():
            raise ValidationError('Slot is already fully booked')
        
        # Update booking
        booking.status = 'confirmed'
        booking.confirmed_at = timezone.now()
        booking.save()
        
        # Update slot capacity
        booking.slot.booked_count += 1
        booking.slot.save()
        
        # TODO: Send notification (when Celery is set up)
        # send_booking_confirmation_email.delay(booking.id)
        
        return booking
    
    @staticmethod
    @transaction.atomic
    def cancel_booking(booking, reason=''):
        """
        Cancel a booking (whether pending or confirmed).
        
        Args:
            booking: ServiceBooking instance
            reason: Optional cancellation reason
            
        Returns:
            ServiceBooking: Cancelled booking instance
            
        Raises:
            ValidationError: If booking cannot be cancelled
        """
        # Validate booking status
        if booking.status not in ['pending', 'confirmed']:
            raise ValidationError(f'Only pending or confirmed bookings can be cancelled. Current status: {booking.status}')
        
        was_confirmed = booking.status == 'confirmed'
        
        # Update booking
        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()
        booking.save()
        
        # Update slot capacity if it was confirmed
        if was_confirmed:
            booking.slot.booked_count = max(0, booking.slot.booked_count - 1)
            booking.slot.save()
        
        # TODO: Send notification (when Celery is set up)
        # send_booking_cancellation_email.delay(booking.id, reason)
        
        return booking
    
    @staticmethod
    @transaction.atomic
    def create_booking(slot, pet, tutor, notes=''):
        """
        Create a new booking request.
        
        Args:
            slot: ServiceSlot instance
            pet: Pet instance
            tutor: Tutor instance
            notes: Optional booking notes
            
        Returns:
            ServiceBooking: Created booking instance
            
        Raises:
            ValidationError: If booking cannot be created
        """
        # Validate business scoping
        if pet.business != slot.business:
            raise ValidationError('Pet and slot must belong to the same business')
        
        if tutor.business != pet.business:
            raise ValidationError('Tutor and pet must belong to the same business')
        
        # Validate slot availability
        if not slot.is_available:
            raise ValidationError('Slot is not available')
        
        if slot.is_fully_booked():
            raise ValidationError('Slot is already fully booked')
        
        # Check if pet already has a booking for this slot
        existing_booking = ServiceBooking.objects.filter(slot=slot, pet=pet, status__in=['pending', 'confirmed']).first()
        if existing_booking:
            raise ValidationError('Pet already has a booking for this slot')
        
        # Create booking
        booking = ServiceBooking.objects.create(
            slot=slot,
            pet=pet,
            tutor=tutor,
            notes=notes,
            status='pending'
        )
        
        # TODO: Send notification (when Celery is set up)
        # send_booking_request_email.delay(booking.id)
        
        return booking

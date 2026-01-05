"""
Custom managers and querysets for reservations app
"""
from django.db import models
from django.utils import timezone
from datetime import timedelta


class ServiceBookingQuerySet(models.QuerySet):
    """Custom queryset for ServiceBooking model"""
    
    def for_business(self, business):
        """Filter bookings by business (through pet)"""
        return self.filter(pet__business=business)
    
    def for_pet(self, pet):
        """Filter bookings for a specific pet"""
        return self.filter(pet=pet)
    
    def for_tutor(self, tutor):
        """Filter bookings for a specific tutor"""
        return self.filter(tutor=tutor)
    
    def pending(self):
        """Filter for pending bookings"""
        return self.filter(status='pending')
    
    def confirmed(self):
        """Filter for confirmed bookings"""
        return self.filter(status='confirmed')
    
    def upcoming(self, days_ahead=30):
        """Filter for upcoming bookings"""
        today = timezone.now().date()
        future_date = today + timedelta(days=days_ahead)
        return self.filter(
            slot__date__gte=today,
            slot__date__lte=future_date,
            status__in=['pending', 'confirmed']
        )
    
    def with_related(self):
        """Prefetch related objects for performance"""
        return self.select_related(
            'slot', 'slot__service', 'pet', 'tutor', 'pet__business'
        )


class ServiceBookingManager(models.Manager):
    """Custom manager for ServiceBooking model"""
    
    def get_queryset(self):
        return ServiceBookingQuerySet(self.model, using=self._db)
    
    def for_business(self, business):
        """Get bookings for a specific business"""
        return self.get_queryset().for_business(business)
    
    def for_pet(self, pet):
        """Get bookings for a specific pet"""
        return self.get_queryset().for_pet(pet)
    
    def for_tutor(self, tutor):
        """Get bookings for a specific tutor"""
        return self.get_queryset().for_tutor(tutor)
    
    def pending(self):
        """Get pending bookings"""
        return self.get_queryset().pending()
    
    def confirmed(self):
        """Get confirmed bookings"""
        return self.get_queryset().confirmed()
    
    def upcoming(self, days_ahead=30):
        """Get upcoming bookings"""
        return self.get_queryset().upcoming(days_ahead)
    
    def with_related(self):
        """Get bookings with related objects prefetched"""
        return self.get_queryset().with_related()


class ServiceSlotQuerySet(models.QuerySet):
    """Custom queryset for ServiceSlot model"""
    
    def for_business(self, business):
        """Filter slots by business"""
        return self.filter(business=business)
    
    def available(self):
        """Filter for available slots"""
        return self.filter(is_available=True)
    
    def for_date_range(self, start_date, end_date):
        """Filter slots in date range"""
        return self.filter(date__gte=start_date, date__lte=end_date)
    
    def upcoming(self, days_ahead=30):
        """Filter for upcoming slots"""
        today = timezone.now().date()
        future_date = today + timedelta(days=days_ahead)
        return self.filter(
            date__gte=today,
            date__lte=future_date,
            is_available=True
        )
    
    def with_related(self):
        """Select related service for performance"""
        return self.select_related('service', 'business')


class ServiceSlotManager(models.Manager):
    """Custom manager for ServiceSlot model"""
    
    def get_queryset(self):
        return ServiceSlotQuerySet(self.model, using=self._db)
    
    def for_business(self, business):
        """Get slots for a specific business"""
        return self.get_queryset().for_business(business)
    
    def available(self):
        """Get available slots"""
        return self.get_queryset().available()
    
    def for_date_range(self, start_date, end_date):
        """Get slots in date range"""
        return self.get_queryset().for_date_range(start_date, end_date)
    
    def upcoming(self, days_ahead=30):
        """Get upcoming slots"""
        return self.get_queryset().upcoming(days_ahead)
    
    def with_related(self):
        """Get slots with related objects prefetched"""
        return self.get_queryset().with_related()

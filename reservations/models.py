from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta

class CheckIn(models.Model):
    pet = models.OneToOneField('pets.Pet', on_delete=models.CASCADE)  # ✅ String reference
    is_present = models.BooleanField(default=False)
    checkin_time = models.DateTimeField(null=True, blank=True)
    checkout_time = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        status = '✅ In' if self.is_present else '❌ Out'
        return f"{self.pet.name} - {status}"
    
    def get_status_display(self):
        if self.is_present:
            return f"✅ In since {self.checkin_time.strftime('%H:%M') if self.checkin_time else 'Now'}"
        else:
            return f"❌ Out since {self.checkout_time.strftime('%H:%M') if self.checkout_time else 'Never'}"


class PetAttendance(models.Model):
    """Track which days a pet attended daycare"""
    pet = models.ForeignKey('pets.Pet', on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()  # The day they attended
    checkin_time = models.TimeField(null=True, blank=True)
    checkout_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)  # e.g., "played fetch", "ate well"
    
    class Meta:
        unique_together = ('pet', 'date')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.pet.name} - {self.date}"


class Service(models.Model):
    """Service types available (Grooming, Training, Walks, etc.)"""
    SERVICE_TYPES = [
        ('grooming', 'Grooming'),
        ('training', 'Training'),
        ('walk', 'Walk'),
        ('daycare', 'Daycare'),
        ('checkup', 'Vet Checkup'),
        ('bath', 'Bath'),
        ('nails', 'Nail Trim'),
        ('other', 'Other'),
    ]
    
    type = models.CharField(max_length=20, choices=SERVICE_TYPES, unique=True)
    duration_minutes = models.IntegerField(default=60)  # Default duration for this service
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['type']
    
    def __str__(self):
        return f"{self.get_type_display()}"
    
    def get_type_display(self):
        return dict(self.SERVICE_TYPES).get(self.type, self.type)


class ServiceSlot(models.Model):
    """Available time slots for services that can be booked"""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_capacity = models.IntegerField(default=1)  # How many pets can book this slot
    booked_count = models.IntegerField(default=0)  # Current bookings
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ('service', 'date', 'start_time')
    
    def __str__(self):
        return f"{self.service.type.title()} - {self.date} {self.start_time}"
    
    def is_fully_booked(self):
        return self.booked_count >= self.max_capacity
    
    def available_spots(self):
        return self.max_capacity - self.booked_count


class ServiceBooking(models.Model):
    """Booking request from tutor for a service"""
    STATUS_CHOICES = [
        ('pending', 'Pending Staff Approval'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    slot = models.ForeignKey(ServiceSlot, on_delete=models.CASCADE, related_name='bookings')
    pet = models.ForeignKey('pets.Pet', on_delete=models.CASCADE, related_name='service_bookings')
    tutor = models.ForeignKey('pets.Tutor', on_delete=models.CASCADE, related_name='service_bookings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)  # Special requests
    requested_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-requested_at']
        unique_together = ('slot', 'pet')  # Each pet can only book a slot once
    
    def __str__(self):
        return f"{self.pet.name} - {self.slot.service.type.title()} on {self.slot.date} ({self.status})"
    
    def confirm(self):
        """Staff confirms the booking"""
        if self.status == 'pending':
            self.status = 'confirmed'
            self.confirmed_at = timezone.now()
            self.slot.booked_count += 1
            self.slot.save()
            self.save()
    
    def cancel(self):
        """Cancel the booking (whether pending or confirmed)"""
        if self.status in ['pending', 'confirmed']:
            if self.status == 'confirmed':
                self.slot.booked_count -= 1
                self.slot.save()
            self.status = 'cancelled'
            self.cancelled_at = timezone.now()
            self.save()


class PetReservation(models.Model):
    """Legacy: Track future reservations and grooming appointments (keeping for backward compatibility)"""
    RESERVATION_TYPES = [
        ('daycare', 'Daycare'),
        ('grooming', 'Grooming'),
        ('checkup', 'Vet Checkup'),
        ('training', 'Training'),
        ('other', 'Other'),
    ]
    
    pet = models.ForeignKey('pets.Pet', on_delete=models.CASCADE, related_name='reservations')
    type = models.CharField(max_length=20, choices=RESERVATION_TYPES, default='daycare')
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date', 'time']
    
    def __str__(self):
        return f"{self.pet.name} - {self.type.title()} on {self.date}"


class TutorSchedule(models.Model):
    """Schedule items created by tutors (walks, grooming, daycare, pick-ups/drop-offs)"""
    SCHEDULE_TYPES = [
        ('walk', 'Walk'),
        ('grooming', 'Grooming'),
        ('daycare', 'Daycare'),
        ('pickup', 'Pick-up'),
        ('dropoff', 'Drop-off'),
        ('training', 'Training'),
        ('other', 'Other'),
    ]
    
    pet = models.ForeignKey('pets.Pet', on_delete=models.CASCADE, related_name='tutor_schedule')
    tutor = models.ForeignKey('pets.Tutor', on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=SCHEDULE_TYPES, default='walk')
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.pet.name} - {self.type.title()} on {self.date}"

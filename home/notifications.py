"""
Simple notification system for pet app
Tracks: bookings, messages (woofs), check-ins, etc.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Notification(models.Model):
    """Notifications for users (staff, tutors, app users)"""
    
    NOTIFICATION_TYPES = [
        ('booking_created', 'Booking Created'),
        ('booking_confirmed', 'Booking Confirmed'),
        ('booking_rejected', 'Booking Rejected'),
        ('woof_created', 'New Message'),
        ('woof_reply', 'Message Reply'),
        ('checkin', 'Pet Check-in'),
        ('invitation', 'Invitation Received'),
        ('system', 'System Notification'),
    ]
    
    # Who gets the notification
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    # What happened
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Links to relevant objects (optional)
    content_type = models.CharField(max_length=50, blank=True)  # 'booking', 'woof', 'pet', etc
    object_id = models.IntegerField(null=True, blank=True)
    
    # Metadata
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user.username}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


def create_notification(user, notification_type, title, message, content_type=None, object_id=None):
    """Helper function to create notifications"""
    return Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        content_type=content_type,
        object_id=object_id,
    )


def notify_booking_created(booking, tutor_name):
    """Notify staff when tutor creates a booking"""
    from pets.models import Staff
    
    # Notify all staff in this business
    staff_members = Staff.objects.filter(business=booking.pet.business)
    
    for staff in staff_members:
        create_notification(
            user=staff.user,
            notification_type='booking_created',
            title=f'📅 New Booking Request',
            message=f'{tutor_name} booked {booking.pet.name} for {booking.slot.service.get_type_display()} on {booking.slot.date.strftime("%B %d")} at {booking.slot.start_time.strftime("%H:%M")}',
            content_type='booking',
            object_id=booking.id,
        )


def notify_woof_created(woof, author_name):
    """Notify pet tutors when staff posts a woof"""
    from pets.models import Tutor
    
    # Notify all tutors assigned to this pet
    tutors = Tutor.objects.filter(pets=woof.pet)
    
    for tutor in tutors:
        create_notification(
            user=tutor.user,
            notification_type='woof_created',
            title=f'💬 New Message about {woof.pet.name}',
            message=woof.message[:100] + ('...' if len(woof.message) > 100 else ''),
            content_type='woof',
            object_id=woof.id,
        )


def notify_woof_reply(parent_woof, reply_author_name):
    """Notify when someone replies to a woof"""
    from pets.models import Staff, Tutor
    
    # Notify the original author
    if parent_woof.staff:
        create_notification(
            user=parent_woof.staff,
            notification_type='woof_reply',
            title=f'💬 Reply to your message about {parent_woof.pet.name}',
            message=f'{reply_author_name} replied',
            content_type='woof',
            object_id=parent_woof.id,
        )
    elif parent_woof.tutor:
        create_notification(
            user=parent_woof.tutor.user,
            notification_type='woof_reply',
            title=f'💬 Reply to your message about {parent_woof.pet.name}',
            message=f'{reply_author_name} replied',
            content_type='woof',
            object_id=parent_woof.id,
        )
    
    # Notify all tutors of the pet (except the replier)
    tutors = Tutor.objects.filter(pets=parent_woof.pet)
    for tutor in tutors:
        if tutor != parent_woof.tutor:
            create_notification(
                user=tutor.user,
                notification_type='woof_reply',
                title=f'💬 New message about {parent_woof.pet.name}',
                message=f'{reply_author_name} replied',
                content_type='woof',
                object_id=parent_woof.id,
            )


def notify_checkin(pet, staff_name):
    """Notify tutors when pet checks in"""
    from pets.models import Tutor
    
    tutors = Tutor.objects.filter(pets=pet)
    for tutor in tutors:
        create_notification(
            user=tutor.user,
            notification_type='checkin',
            title=f'✅ {pet.name} Checked In',
            message=f'{staff_name} checked in {pet.name}',
            content_type='pet',
            object_id=pet.id,
        )

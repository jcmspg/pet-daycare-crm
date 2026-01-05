from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.utils import timezone
from pets.models import Business
import uuid

class Invitation(models.Model):
    """Invitation tokens for tutors and staff to join"""
    ROLE_CHOICES = (
        ('staff', 'Staff'),
        ('tutor', 'Tutor/Pet Parent'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    used_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='invitations_used')
    
    class Meta:
        unique_together = ('business', 'email')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()}) - {self.business.name}"
    
    @property
    def is_used(self):
        return self.used_at is not None
    
    @property
    def is_valid(self):
        """Invitation is valid if not used yet"""
        return not self.is_used


class BusinessInquiry(models.Model):
    """Inquiry from potential business customers"""
    business_name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    num_locations = models.IntegerField(null=True, blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    contacted = models.BooleanField(default=False)
    contacted_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Business Inquiries"
    
    def __str__(self):
        return f"{self.business_name} - {self.email}"


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

from django.db import models
from django.contrib.auth.models import User
from .managers import PetManager, TutorManager, StaffManager

class Business(models.Model):
    name = models.CharField(max_length=100)
    banner_image = models.ImageField(upload_to='business_banners/', null=True, blank=True)
    
    def __str__(self):
        return self.name


class FooterConfig(models.Model):
    """Customizable footer configuration for each business"""
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name='footer_config')
    
    # Brand info
    brand_name = models.CharField(max_length=100, default='PawCentral')
    tagline = models.CharField(max_length=255, blank=True, default='Trusted pet care service')
    
    # Contact info
    email = models.EmailField(blank=True, default='support@pawcentral.com')
    phone = models.CharField(max_length=20, blank=True, default='+1 (555) 123-4567')
    hours = models.CharField(max_length=100, blank=True, default='Mon-Fri 9 AM - 5 PM')
    
    # Social links
    facebook_url = models.URLField(blank=True, default='#')
    instagram_url = models.URLField(blank=True, default='#')
    twitter_url = models.URLField(blank=True, default='#')
    
    # Footer text
    copyright_text = models.CharField(max_length=255, blank=True, default='All rights reserved. Built with ❤️ for pet lovers')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Footer Config - {self.business.name}"
    
    class Meta:
        verbose_name = "Footer Configuration"
        verbose_name_plural = "Footer Configurations"

class Staff(models.Model):
    """Staff members associated with a business"""
    ROLE_CHOICES = (
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='staff_members')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    
    objects = StaffManager()
    
    class Meta:
        unique_together = ('user', 'business')
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email} - {self.business.name}"
    
    @property
    def is_manager(self):
        """Check if this staff member is a manager"""
        return self.role == 'manager'
    
    def can_manage_staff(self):
        """Check if user can manage other staff members"""
        return self.is_manager
    
    def can_manage_payments(self):
        """Check if user can manage payments and billing"""
        return self.is_manager

class Tutor(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='tutors')
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='tutor_profile')
    
    objects = TutorManager()
    
    def __str__(self):
        return self.name

class Pet(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='pet_photos/', blank=True, null=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='pets')
    tutors = models.ManyToManyField(Tutor, related_name='pets')
    notes = models.TextField(blank=True)
    # New metadata fields
    birthday = models.DateField(null=True, blank=True)
    species = models.CharField(max_length=50, blank=True)
    breed = models.CharField(max_length=100, blank=True)
    SEX_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('unknown', 'Unknown'),
    )
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, default='unknown')
    neutered = models.BooleanField(default=False)
    allergies = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    chip_number = models.CharField(max_length=64, blank=True)
    
    objects = PetManager()

class TrainingProgress(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='training_entries')
    date = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    progress = models.PositiveSmallIntegerField(default=0)  # 0-100

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.pet.name} - {self.title} ({self.progress}%)"

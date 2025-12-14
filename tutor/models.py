from django.db import models
from pets.models import Pet

# Create your models here.
class PetPhoto(models.Model):
    pet = models.ForeignKey('pets.Pet', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='pet_photos/')
    caption = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)

class Woof(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    message = models.CharField(max_length=280)  # Twitter limit
    created_at = models.DateTimeField(auto_now_add=True)
    staff = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    tutor = models.ForeignKey('pets.Tutor', on_delete=models.CASCADE, null=True, blank=True)
    parent_woof = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    attachment = models.FileField(upload_to='woof_attachments/', null=True, blank=True)
    VISIBILITY_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private (to pet tutor)')
    )
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')

class WoofLog(models.Model):
    woof = models.ForeignKey(Woof, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)  # "created", "replied"
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True)

class GlobalWoof(models.Model):
    message = models.CharField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)
    staff = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    attachment = models.FileField(upload_to='woof_attachments/', null=True, blank=True)

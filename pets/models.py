from django.db import models

class Business(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Tutor(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='tutors')
    
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
    
    def __str__(self):
        return f"{self.name}"

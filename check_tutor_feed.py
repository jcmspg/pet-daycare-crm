import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'petcrm.settings')
django.setup()

from pets.models import Tutor, Pet
from tutor.models import Woof, GlobalWoof
from django.db.models import Q

# Check tutor data
tutors = Tutor.objects.all()
print(f'📊 Total Tutors: {tutors.count()}')

for tutor in tutors:
    print(f'\n=== Tutor: {tutor.user.username} ({tutor.business}) ===')
    
    # Get tutor's pets (ManyToMany relationship)
    pets = tutor.pets.all()
    print(f'Pets: {pets.count()}')
    for pet in pets:
        print(f'  - {pet.name} (Business: {pet.business})')
    
    # Check woofs for these pets
    if pets.exists():
        pet_woofs = Woof.objects.filter(
            business=tutor.business,
            pet__in=pets,
            parent_woof__isnull=True
        ).filter(
            Q(visibility='public') | Q(visibility='private')
        )
        print(f'Woofs for tutor\'s pets: {pet_woofs.count()}')
        for w in pet_woofs[:3]:
            print(f'  - Woof {w.id}: {w.message[:50]}')
    
    # Check global woofs
    global_woofs = GlobalWoof.objects.filter(business=tutor.business)
    print(f'Global woofs for business: {global_woofs.count()}')

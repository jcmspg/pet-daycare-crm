from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import connection
from pets.models import Business, Staff, Tutor, Pet
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Seed database with test data: 2 businesses, staff, 10 tutors, and populated pets'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Starting database seeding...')
        
        # Clear all data
        self.stdout.write('🗑️  Clearing existing data...')
        Pet.objects.all().delete()
        Tutor.objects.all().delete()
        Staff.objects.all().delete()
        Business.objects.all().delete()
        User.objects.filter(is_staff=False, is_superuser=False).delete()
        # Also delete the staff/tutor users
        User.objects.filter(username__startswith='staff').delete()
        User.objects.filter(username__startswith='tutor').delete()
        
        # Create businesses
        self.stdout.write('🏢 Creating businesses...')
        business1 = Business.objects.create(name='Tails Daycare')
        business2 = Business.objects.create(name='Paws & Love')
        self.stdout.write(f'  ✓ {business1.name}')
        self.stdout.write(f'  ✓ {business2.name}')
        
        # Create staff members for each business
        self.stdout.write('👨‍💼 Creating staff members...')
        
        # Business 1 staff
        staff1_user = User.objects.create_user(
            username='staff1_manager@somemail.com',
            email='staff1_manager@somemail.com',
            password='SecurePass123!',
            first_name='Alice',
            last_name='Manager'
        )
        staff1_mgr = Staff.objects.create(
            user=staff1_user,
            business=business1,
            role='manager'
        )
        self.stdout.write(f'  ✓ Alice (Manager) - {business1.name}')
        
        staff2_user = User.objects.create_user(
            username='staff2_staff@somemail.com',
            email='staff2_staff@somemail.com',
            password='SecurePass123!',
            first_name='Bob',
            last_name='Staff'
        )
        staff2_staff = Staff.objects.create(
            user=staff2_user,
            business=business1,
            role='staff'
        )
        self.stdout.write(f'  ✓ Bob (Staff) - {business1.name}')
        
        # Business 2 staff
        staff3_user = User.objects.create_user(
            username='staff3_manager@somemail.com',
            email='staff3_manager@somemail.com',
            password='SecurePass123!',
            first_name='Carol',
            last_name='Manager'
        )
        staff3_mgr = Staff.objects.create(
            user=staff3_user,
            business=business2,
            role='manager'
        )
        self.stdout.write(f'  ✓ Carol (Manager) - {business2.name}')
        
        staff4_user = User.objects.create_user(
            username='staff4_staff@somemail.com',
            email='staff4_staff@somemail.com',
            password='SecurePass123!',
            first_name='Diana',
            last_name='Staff'
        )
        staff4_staff = Staff.objects.create(
            user=staff4_user,
            business=business2,
            role='staff'
        )
        self.stdout.write(f'  ✓ Diana (Staff) - {business2.name}')
        
        # Create tutors
        self.stdout.write('👨‍👩‍👧‍👦 Creating 10 tutors...')
        tutors = []
        for i in range(1, 11):
            email = f'tutor{i}@somemail.com'
            user = User.objects.create_user(
                username=email,
                email=email,
                password='SecurePass123!'
            )
            business = business1 if i <= 5 else business2  # Split between businesses
            tutor = Tutor.objects.create(
                name=f'Pet Parent {i}',
                phone=f'555-{1000+i:04d}',
                email=email,
                address=f'{i} Main Street, Pet City',
                business=business,
                user=user  # Link user to tutor
            )
            tutors.append(tutor)
            self.stdout.write(f'  ✓ {tutor.name} ({email})')
        
        # Pet data
        pet_names = [
            'Max', 'Bella', 'Charlie', 'Lucy', 'Cooper', 'Daisy', 'Rocky', 'Luna',
            'Bailey', 'Buddy', 'Molly', 'Duke', 'Sadie', 'Rex', 'Lola', 'Oliver',
            'Sophie', 'Tucker', 'Maggie', 'Simba', 'Chloe', 'Toby', 'Zoe', 'Jake',
            'Emma', 'Leo', 'Milo', 'Penny', 'Scout', 'Bear'
        ]
        
        breeds = [
            'Labrador Retriever', 'Golden Retriever', 'German Shepherd', 'Bulldog',
            'Poodle', 'Beagle', 'Yorkshire Terrier', 'Dachshund', 'Boxer', 'Siberian Husky',
            'Cocker Spaniel', 'Rottweiler', 'Shih Tzu', 'Maltese', 'Great Dane'
        ]
        
        # Create pets and assign to tutors
        self.stdout.write('🐕 Creating and assigning pets...')
        pet_count = 0
        for tutor in tutors:
            # Random number of pets: 1-3, with most having 1-2
            num_pets = random.choices([1, 2, 3], weights=[40, 45, 15])[0]
            
            for _ in range(num_pets):
                pet_name = random.choice(pet_names)
                pet = Pet.objects.create(
                    name=pet_name,
                    business=tutor.business,
                    species='Dog',
                    breed=random.choice(breeds),
                    sex=random.choice(['male', 'female']),
                    birthday=timezone.now().date() - timedelta(days=random.randint(365, 2555)),
                    neutered=random.choice([True, False]),
                    notes=f'Happy {pet_name} living at {tutor.business.name}'
                )
                pet.tutors.add(tutor)
                pet_count += 1
                self.stdout.write(f'  ✓ {pet_name} assigned to {tutor.name}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Database seeded successfully!'))
        self.stdout.write(f'\n📊 Summary:')
        self.stdout.write(f'  Businesses: 2')
        self.stdout.write(f'  Staff: 4 (2 per business)')
        self.stdout.write(f'  Tutors: 10')
        self.stdout.write(f'  Pets: {pet_count}')
        self.stdout.write(f'\n🔐 Staff Accounts:')
        self.stdout.write(f'\n  Tails Daycare:')
        self.stdout.write(f'    staff1_manager@somemail.com / SecurePass123! (Manager)')
        self.stdout.write(f'    staff2_staff@somemail.com / SecurePass123! (Staff)')
        self.stdout.write(f'\n  Paws & Love:')
        self.stdout.write(f'    staff3_manager@somemail.com / SecurePass123! (Manager)')
        self.stdout.write(f'    staff4_staff@somemail.com / SecurePass123! (Staff)')
        self.stdout.write(f'\n🔐 Tutor Accounts:')
        for i in range(1, 11):
            self.stdout.write(f'  tutor{i}@somemail.com / SecurePass123!')

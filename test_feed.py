import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'petcrm.settings')
django.setup()

from pets.models import Tutor
from tutor.models import Woof, GlobalWoof
from django.db.models import Q

# Test for a specific tutor
tutor = Tutor.objects.filter(user__email='joaocmspgomes@gmail.com').first()
if not tutor:
    print('❌ Tutor not found')
    exit()

print(f'✅ Testing feed for: {tutor.user.username} ({tutor.business})')

business = tutor.business
pets = tutor.pets.all()

print(f'\n📊 Pets: {pets.count()}')
for pet in pets:
    print(f'  - {pet.name}')

# Build feed like the view does
pet_woofs = Woof.objects.filter(
    business=business,
    pet__in=pets, 
    parent_woof__isnull=True
).filter(
    Q(visibility='public') | Q(visibility='private')
)

print(f'\n📊 Pet Woofs Query:')
print(f'  Count: {pet_woofs.count()}')
for w in pet_woofs:
    print(f'  - Woof {w.id}: {w.message[:50]}')

global_woofs = GlobalWoof.objects.filter(business=business)
print(f'\n📊 Global Woofs Query:')
print(f'  Count: {global_woofs.count()}')

feed = []
for w in pet_woofs:
    feed.append({
        'kind': 'pet',
        'label': w.pet.name,
        'created_at': w.created_at,
        'message': w.message,
    })
for gw in global_woofs:
    feed.append({
        'kind': 'business',
        'label': 'BUSINESS',
        'created_at': gw.created_at,
        'message': gw.message,
    })

print(f'\n📊 Final Feed:')
print(f'  Length: {len(feed)}')
print(f'  Empty?: {not feed}')
print(f'  Bool: {bool(feed)}')

if feed:
    print('\n✅ Feed has items!')
else:
    print('\n❌ Feed is empty!')

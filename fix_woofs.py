import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'petcrm.settings')
django.setup()

from tutor.models import Woof, GlobalWoof

# Fix woofs without business - infer from pet
woofs_fixed = 0
for woof in Woof.objects.filter(business__isnull=True):
    if woof.pet and woof.pet.business:
        woof.business = woof.pet.business
        woof.save()
        woofs_fixed += 1

print(f'✅ Fixed {woofs_fixed} woofs without business field')

# Check globals
globals_no_business = GlobalWoof.objects.filter(business__isnull=True).count()
print(f'⚠️  GlobalWoofs without business: {globals_no_business}')

# Check totals
print(f'\n📊 Total Woofs: {Woof.objects.count()}')
print(f'📊 Total GlobalWoofs: {GlobalWoof.objects.count()}')

# Show sample woofs
print('\n=== Sample Woofs ===')
for w in Woof.objects.all()[:3]:
    print(f'  ID: {w.id}, Pet: {w.pet.name if w.pet else "No pet"}, Business: {w.business}, Message: {w.message[:50] if w.message else "No message"}')

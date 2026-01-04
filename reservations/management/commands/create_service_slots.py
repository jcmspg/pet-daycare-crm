from django.core.management.base import BaseCommand
from reservations.utils import ensure_service_slots_exist

class Command(BaseCommand):
    help = 'Create service slots for the next 30 days'

    def handle(self, *args, **options):
        result = ensure_service_slots_exist()
        
        if result:
            self.stdout.write('✓ Created new service slots for next 30 days')
        else:
            self.stdout.write('✓ Service slots already exist for next 30 days (no new slots created)')


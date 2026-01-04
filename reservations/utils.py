"""Utility functions for reservations"""
from datetime import datetime, timedelta, time
from .models import ServiceSlot, Service
from pets.models import Business


def ensure_service_slots_exist(business=None):
    """
    Automatically create service slots for the next 30 days if they don't exist.
    This is called automatically when tutors load the dashboard.
    
    If business is None, creates slots for all businesses.
    """
    today = datetime.now().date()
    end_date = today + timedelta(days=29)
    
    # Get businesses to create slots for
    if business:
        businesses = [business]
    else:
        businesses = Business.objects.all()
    
    services = Service.objects.all()
    
    # Define time slots for each service type
    slot_config = {
        'daycare': [
            (time(8, 0), time(12, 0), 5),    # Morning: 8am-12pm, 5 spots
            (time(14, 0), time(18, 0), 5),   # Afternoon: 2pm-6pm, 5 spots
        ],
        'grooming': [
            (time(9, 0), time(11, 0), 1),    # Slot 1: 9am-11am, 1 spot
            (time(11, 0), time(13, 0), 1),   # Slot 2: 11am-1pm, 1 spot
            (time(14, 0), time(16, 0), 1),   # Slot 3: 2pm-4pm, 1 spot
            (time(16, 0), time(18, 0), 1),   # Slot 4: 4pm-6pm, 1 spot
        ],
        'training': [
            (time(10, 0), time(11, 0), 2),   # Slot 1: 10am-11am, 2 spots
            (time(14, 0), time(15, 0), 2),   # Slot 2: 2pm-3pm, 2 spots
            (time(15, 0), time(16, 0), 2),   # Slot 3: 3pm-4pm, 2 spots
        ],
        'walk': [
            (time(8, 0), time(9, 0), 3),     # Slot 1: 8am-9am, 3 spots
            (time(10, 0), time(11, 0), 3),   # Slot 2: 10am-11am, 3 spots
            (time(14, 0), time(15, 0), 3),   # Slot 3: 2pm-3pm, 3 spots
            (time(16, 0), time(17, 0), 3),   # Slot 4: 4pm-5pm, 3 spots
        ],
    }
    
    slots_created = 0
    
    # Create slots for next 30 days for each business
    for biz in businesses:
        for i in range(30):
            date = today + timedelta(days=i)
            
            for service in services:
                config = slot_config.get(service.type, [])
                for start_time, end_time, capacity in config:
                    _, created = ServiceSlot.objects.get_or_create(
                        business=biz,
                        service=service,
                        date=date,
                        start_time=start_time,
                        defaults={
                            'end_time': end_time,
                            'max_capacity': capacity,
                            'booked_count': 0,
                            'is_available': True,
                        }
                    )
                    if created:
                        slots_created += 1
    
    return slots_created > 0  # Return True if new slots were created

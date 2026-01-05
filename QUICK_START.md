# Quick Start Guide - Refactored Codebase

## 🚀 **What Changed?**

Your codebase now has a **solid, scalable foundation** with:
- ✅ Service layer architecture
- ✅ Custom managers for cleaner queries
- ✅ REST API endpoints
- ✅ Celery configuration (ready to enable)
- ✅ Better code organization

## 📦 **Install Dependencies**

```bash
pip install -r requirements.txt
```

## 🔧 **New Code Patterns**

### **1. Using Custom Managers**

**Before:**
```python
pets = Pet.objects.filter(business=business)
bookings = ServiceBooking.objects.filter(status='pending').select_related(...)
```

**After:**
```python
pets = Pet.objects.for_business(business)
bookings = ServiceBooking.objects.for_business(business).pending().with_related()
```

### **2. Using Service Layer**

**Before:**
```python
booking.status = 'confirmed'
booking.save()
```

**After:**
```python
from reservations.services.booking_service import BookingService

try:
    BookingService.confirm_booking(booking, request.user)
except ValidationError as e:
    messages.error(request, str(e))
```

### **3. Using REST API**

**New API Endpoints:**
- `GET /api/reservations/bookings/` - List bookings
- `POST /api/reservations/bookings/{id}/confirm/` - Confirm booking
- `POST /api/reservations/bookings/{id}/cancel/` - Cancel booking
- `GET /api/reservations/slots/` - List service slots

## ⚙️ **Optional: Enable Redis & Celery**

When ready to use background tasks:

1. Install Redis:
```bash
# Ubuntu/Debian
sudo apt install redis-server

# macOS
brew install redis
```

2. Start Redis:
```bash
redis-server
```

3. Uncomment Celery settings in `petcrm/settings.py`:
```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
# ... rest of Celery config
```

4. Start Celery worker:
```bash
celery -A petcrm worker -l info
```

## 📝 **Migration Notes**

- ✅ All existing code still works
- ✅ No breaking changes
- ✅ Backward compatible
- ✅ Can migrate gradually

## 🎯 **Next Steps**

1. Test the new code patterns
2. Gradually migrate other features to services
3. Enable Redis/Celery when ready
4. Build new features using the new architecture

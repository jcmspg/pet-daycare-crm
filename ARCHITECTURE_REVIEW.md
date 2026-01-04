# Backend Architecture Review & Scalability Roadmap
## PawCentral Platform - 2026-01-04

---

## 🔍 CURRENT ARCHITECTURE ANALYSIS

### ✅ **What's Working Well**

1. **Multi-tenant Isolation**: Excellent business-scoped data isolation
2. **Security**: Multi-layer validation, proper authentication
3. **App Structure**: Logical separation by domain (pets, reservations, staff, tutor)
4. **Model Relationships**: Well-defined ForeignKeys and ManyToMany relationships

### ⚠️ **Critical Issues for Scalability**

#### 1. **Fat Views Pattern** (Major Issue)
**Problem**: Business logic is embedded directly in views
- Views are 100-400 lines long
- Complex nested conditionals
- Hard to test, reuse, or maintain
- Mixing presentation with business logic

**Example from `staff/views.py:37-124`**:
```python
if request.method == 'POST':
    action = request.POST.get('action')
    pet_id = request.POST.get('pet_id')
    # ... 80+ lines of business logic in view
```

**Impact**: 
- Cannot reuse booking logic
- Cannot test business logic independently
- Hard to add API endpoints
- Code duplication across views

#### 2. **No Service Layer**
**Problem**: No abstraction between views and models
- Direct ORM calls in views
- Business logic scattered across views
- No centralized business rules

**What's Missing**:
- Service classes (e.g., `BookingService`, `CheckInService`)
- Business rule enforcement
- Transaction management
- Event handling (notifications, webhooks)

#### 3. **Database: SQLite** (Production Killer)
**Problem**: SQLite is fine for dev, terrible for production
- No concurrent writes
- Single file, no replication
- No connection pooling
- Limited scalability
- Migration path unclear

**Must Migrate To**: PostgreSQL (for production)

#### 4. **No API Layer**
**Problem**: Views only render HTML templates
- No REST API for mobile apps
- No GraphQL for flexible queries
- Can't integrate with external services (vets, food brands)
- No webhook support
- Hard to build mobile app

#### 5. **No Background Tasks**
**Problem**: Everything runs synchronously
- No async processing for:
  - Email notifications
  - Vaccine reminders
  - Route optimization
  - Image processing
  - Data aggregation
  - Report generation

**Must Add**: Celery + Redis/RabbitMQ

#### 6. **No Caching**
**Problem**: Every request hits the database
- No Redis/Memcached
- Expensive queries repeated
- No session caching
- Slow dashboard loads

#### 7. **No Custom Managers/QuerySets**
**Problem**: Business logic queries repeated everywhere
- `Pet.objects.filter(business=business)` repeated
- No `Pet.objects.for_business(business)`
- No custom filtering methods
- Hard to optimize queries

#### 8. **No Event System**
**Problem**: Features tightly coupled
- Adding vaccine reminders requires touching multiple files
- No publish/subscribe pattern
- Hard to add integrations
- No audit trail

#### 9. **No API Rate Limiting**
**Problem**: Vulnerable to abuse
- No rate limiting on API endpoints (when added)
- No throttling
- DDoS vulnerability

#### 10. **No Proper Error Handling**
**Problem**: Generic error handling
- Try/except blocks everywhere
- No structured error responses
- Hard to debug production issues
- No error tracking (Sentry)

---

## 🏗️ RECOMMENDED ARCHITECTURE

### **Target Architecture: Layered Service-Oriented**

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│  (Views, API Views, Templates)          │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Service Layer                   │
│  (Business Logic, Transactions)         │
│  - BookingService                       │
│  - CheckInService                       │
│  - MedicalService                       │
│  - RouteService                         │
│  - NotificationService                  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Repository/Manager Layer        │
│  (Data Access, Custom QuerySets)        │
│  - PetManager                           │
│  - BookingManager                       │
│  - BusinessScopedQuerySet               │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Model Layer                     │
│  (Django ORM Models)                    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Database (PostgreSQL)           │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         Background Tasks (Celery)       │
│  - Email notifications                  │
│  - Reminders                            │
│  - Route optimization                   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         External Services               │
│  - Vet APIs                             │
│  - Mapping APIs (Google Maps)           │
│  - Payment processors                   │
│  - SMS providers                        │
└─────────────────────────────────────────┘
```

---

## 📦 PROPOSED CODE STRUCTURE

### **1. Service Layer** (`pets/services/`, `reservations/services/`)

```python
# reservations/services/booking_service.py
class BookingService:
    """Centralized booking business logic"""
    
    @staticmethod
    @transaction.atomic
    def create_booking(slot, pet, tutor, notes=''):
        """Create a booking with validation"""
        # Validate business scoping
        # Check capacity
        # Create booking
        # Send notifications
        # Return booking
    
    @staticmethod
    def confirm_booking(booking, staff):
        """Confirm booking with notifications"""
    
    @staticmethod
    def cancel_booking(booking, reason=''):
        """Cancel booking with cleanup"""

# pets/services/medical_service.py
class MedicalService:
    """Medical records and vaccine management"""
    
    @staticmethod
    def record_vaccine(pet, vaccine_type, date, vet=None):
        """Record a vaccine"""
    
    @staticmethod
    def get_upcoming_reminders(business, days_ahead=30):
        """Get pets needing vaccines"""
    
    @staticmethod
    def create_medical_report(pet, report_type, data):
        """Create medical report"""

# reservations/services/route_service.py
class RouteService:
    """Pickup/delivery route optimization"""
    
    @staticmethod
    def optimize_routes(pickups, date):
        """Optimize pickup/delivery routes"""
        # Use Google Maps API or route optimization library
    
    @staticmethod
    def assign_driver(route, driver):
        """Assign driver to route"""
```

### **2. Custom Managers** (`pets/managers.py`)

```python
# pets/managers.py
class BusinessScopedQuerySet(models.QuerySet):
    """Base queryset that filters by business"""
    
    def for_business(self, business):
        return self.filter(business=business)
    
    def active(self):
        return self.filter(is_active=True)

class PetQuerySet(BusinessScopedQuerySet):
    def with_vaccines(self):
        return self.prefetch_related('vaccines')
    
    def needing_vaccines(self, days_ahead=30):
        # Complex query for pets needing vaccines
        pass

class PetManager(models.Manager):
    def get_queryset(self):
        return PetQuerySet(self.model, using=self._db)
    
    def for_business(self, business):
        return self.get_queryset().for_business(business)
    
    def needing_vaccines(self, business, days_ahead=30):
        return self.for_business(business).needing_vaccines(days_ahead)

class Pet(models.Model):
    objects = PetManager()
    # ... fields
```

### **3. API Layer** (`pets/api/`, `reservations/api/`)

```python
# reservations/api/serializers.py (DRF)
from rest_framework import serializers

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceBooking
        fields = ['id', 'slot', 'pet', 'status', 'notes']

# reservations/api/views.py (DRF)
from rest_framework import viewsets
from rest_framework.decorators import action

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsBusinessMember]
    
    def get_queryset(self):
        business = self.request.user.staff_profile.business
        return ServiceBooking.objects.for_business(business)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        booking = self.get_object()
        BookingService.confirm_booking(booking, request.user)
        return Response({'status': 'confirmed'})
```

### **4. Background Tasks** (`pets/tasks.py`, `reservations/tasks.py`)

```python
# pets/tasks.py
from celery import shared_task

@shared_task
def send_vaccine_reminder(pet_id, vaccine_type, due_date):
    """Send vaccine reminder email/SMS"""
    pet = Pet.objects.get(id=pet_id)
    # Send notification
    pass

@shared_task
def check_upcoming_vaccines():
    """Daily task to check for upcoming vaccines"""
    businesses = Business.objects.all()
    for business in businesses:
        pets_needing = MedicalService.get_upcoming_reminders(business)
        for pet, vaccine in pets_needing:
            send_vaccine_reminder.delay(pet.id, vaccine.type, vaccine.due_date)

# reservations/tasks.py
@shared_task
def optimize_routes_for_date(date):
    """Optimize routes for a specific date"""
    RouteService.optimize_routes_for_date(date)
```

---

## 🚀 FEATURE IMPLEMENTATION PLAN

### **1. NFC Dog Tag Reading**

**Architecture**:
```python
# pets/models.py
class PetTag(models.Model):
    """NFC tag associated with a pet"""
    pet = models.OneToOneField(Pet, on_delete=models.CASCADE, related_name='tag')
    tag_id = models.CharField(max_length=128, unique=True)  # NFC UID
    tag_type = models.CharField(max_length=20, choices=[('nfc', 'NFC'), ('qr', 'QR')])
    registered_at = models.DateTimeField(auto_now_add=True)
    last_scan = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

class TagScan(models.Model):
    """Log of tag scans for check-ins"""
    tag = models.ForeignKey(PetTag, on_delete=models.CASCADE, related_name='scans')
    scanned_by = models.ForeignKey(User, on_delete=models.CASCADE)
    scan_type = models.CharField(max_length=20, choices=[('checkin', 'Check-in'), ('checkout', 'Check-out')])
    scanned_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=200, blank=True)  # GPS/beacon location

# pets/api/nfc.py
class NFCReaderView(APIView):
    """API endpoint for NFC readers"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        tag_id = request.data.get('tag_id')
        scan_type = request.data.get('scan_type', 'checkin')
        
        try:
            tag = PetTag.objects.get(tag_id=tag_id, is_active=True)
            # Verify business access
            if tag.pet.business != request.user.staff_profile.business:
                return Response({'error': 'Unauthorized'}, status=403)
            
            # Create scan record
            TagScan.objects.create(
                tag=tag,
                scanned_by=request.user,
                scan_type=scan_type,
                location=request.data.get('location')
            )
            
            # Trigger check-in/out
            CheckInService.handle_tag_scan(tag.pet, scan_type, request.user)
            
            return Response({
                'pet': tag.pet.name,
                'status': 'success'
            })
        except PetTag.DoesNotExist:
            return Response({'error': 'Tag not found'}, status=404)
```

**Hardware Integration**:
- NFC reader connects to mobile app or web interface
- Mobile app reads NFC → calls API
- Web interface can use NFC reader libraries (Web NFC API)

---

### **2. Medical Reports & Vaccine Reminders**

**Architecture**:
```python
# pets/models.py
class Vaccine(models.Model):
    """Vaccine types"""
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=50)  # dog, cat, etc.
    frequency_days = models.IntegerField()  # Days between shots
    is_required = models.BooleanField(default=False)

class PetVaccine(models.Model):
    """Pet's vaccine records"""
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='vaccines')
    vaccine = models.ForeignKey(Vaccine, on_delete=models.CASCADE)
    administered_date = models.DateField()
    next_due_date = models.DateField()
    vet = models.ForeignKey('VetPartner', on_delete=models.SET_NULL, null=True, blank=True)
    batch_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    document = models.FileField(upload_to='vaccines/', blank=True, null=True)

class MedicalReport(models.Model):
    """Medical reports/records"""
    REPORT_TYPES = [
        ('checkup', 'Check-up'),
        ('treatment', 'Treatment'),
        ('surgery', 'Surgery'),
        ('allergy', 'Allergy'),
        ('medication', 'Medication'),
    ]
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='medical_reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    date = models.DateField()
    vet = models.ForeignKey('VetPartner', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField()
    diagnosis = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    documents = models.ManyToManyField('MedicalDocument', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

# pets/services/medical_service.py
class MedicalService:
    @staticmethod
    def get_upcoming_vaccines(business, days_ahead=30):
        """Get pets needing vaccines in next N days"""
        today = timezone.now().date()
        due_date = today + timedelta(days=days_ahead)
        return PetVaccine.objects.filter(
            pet__business=business,
            next_due_date__lte=due_date,
            next_due_date__gte=today
        ).select_related('pet', 'vaccine')
    
    @staticmethod
    def send_vaccine_reminders(business, days_ahead=7):
        """Send reminders for upcoming vaccines"""
        upcoming = MedicalService.get_upcoming_vaccines(business, days_ahead)
        for pet_vaccine in upcoming:
            send_vaccine_reminder_email.delay(pet_vaccine.id)

# pets/tasks.py
@shared_task
def check_vaccine_reminders():
    """Daily task - check all businesses for upcoming vaccines"""
    businesses = Business.objects.all()
    for business in businesses:
        MedicalService.send_vaccine_reminders(business, days_ahead=7)

# Configure in settings.py
CELERY_BEAT_SCHEDULE = {
    'check-vaccine-reminders': {
        'task': 'pets.tasks.check_vaccine_reminders',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
    },
}
```

---

### **3. Pickup & Delivery Routes**

**Architecture**:
```python
# reservations/models.py
class PickupDelivery(models.Model):
    """Pickup/delivery requests"""
    SERVICE_TYPES = [
        ('pickup', 'Pickup'),
        ('delivery', 'Delivery'),
    ]
    booking = models.OneToOneField(ServiceBooking, on_delete=models.CASCADE, related_name='transport')
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='transports')
    pickup_address = models.CharField(max_length=255)
    delivery_address = models.CharField(max_length=255)
    requested_time = models.DateTimeField()
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='routes')
    status = models.CharField(max_length=20, choices=[...])
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

class Route(models.Model):
    """Optimized route for multiple pickups/deliveries"""
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='routes')
    date = models.DateField()
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    waypoints = models.JSONField()  # Ordered list of addresses
    optimized_sequence = models.JSONField()  # Optimized order
    estimated_duration = models.DurationField(null=True, blank=True)
    estimated_distance = models.FloatField(null=True, blank=True)  # km
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

# reservations/services/route_service.py
import googlemaps
from django.conf import settings

class RouteService:
    def __init__(self):
        self.gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
    
    def optimize_route(self, pickups_deliveries, date):
        """Optimize route using Google Maps API or optimization algorithm"""
        # 1. Get coordinates for all addresses
        # 2. Use Google Maps Distance Matrix API
        # 3. Solve Traveling Salesman Problem (TSP)
        # 4. Create Route object with optimized sequence
        pass
    
    def get_route_directions(self, route):
        """Get turn-by-turn directions"""
        waypoints = route.waypoints
        origin = waypoints[0]
        destination = waypoints[-1]
        return self.gmaps.directions(origin, destination, waypoints=waypoints[1:-1])
```

**Libraries Needed**:
- `googlemaps` - Google Maps API
- `ortools` - Route optimization (TSP solver)
- Or `scipy.optimize` for simpler optimization

---

### **4. Partnerships (Vets, Pet Food Brands)**

**Architecture**:
```python
# partnerships/models.py (NEW APP)
class PartnerType(models.TextChoices):
    VET = 'vet', 'Veterinarian'
    FOOD_BRAND = 'food_brand', 'Pet Food Brand'
    GROOMER = 'groomer', 'Groomer'
    PET_STORE = 'pet_store', 'Pet Store'

class Partner(models.Model):
    """External partners (vets, food brands, etc.)"""
    name = models.CharField(max_length=200)
    partner_type = models.CharField(max_length=20, choices=PartnerType.choices)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='partners', null=True, blank=True)
    # Global partners (food brands) have no business
    # Local partners (vets) are business-specific
    
    # Contact info
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    
    # API integration
    api_key = models.CharField(max_length=255, blank=True)
    api_endpoint = models.URLField(blank=True)
    is_integrated = models.BooleanField(default=False)
    
    # Settings
    sync_vaccines = models.BooleanField(default=False)
    sync_medical_reports = models.BooleanField(default=False)
    auto_import = models.BooleanField(default=False)

class VetPartner(Partner):
    """Veterinarian partner"""
    clinic_name = models.CharField(max_length=200)
    license_number = models.CharField(max_length=100, blank=True)
    
    class Meta:
        proxy = False

# partnerships/services/integration_service.py
class VetIntegrationService:
    """Service to sync with vet APIs"""
    
    @staticmethod
    def sync_pet_vaccines(pet, vet_partner):
        """Sync vaccines from vet system"""
        if not vet_partner.is_integrated:
            return
        
        # Call vet API
        response = requests.get(
            f"{vet_partner.api_endpoint}/pets/{pet.chip_number}/vaccines",
            headers={'Authorization': f'Bearer {vet_partner.api_key}'}
        )
        
        # Import vaccines
        for vaccine_data in response.json():
            PetVaccine.objects.update_or_create(
                pet=pet,
                vaccine__name=vaccine_data['type'],
                defaults={
                    'administered_date': vaccine_data['date'],
                    'next_due_date': vaccine_data['next_due'],
                    'vet': vet_partner,
                }
            )
    
    @staticmethod
    def sync_medical_reports(pet, vet_partner):
        """Sync medical reports from vet"""
        # Similar implementation
        pass

# pets/models.py - Add to Pet model
class Pet(models.Model):
    # ... existing fields
    preferred_vet = models.ForeignKey('partnerships.VetPartner', on_delete=models.SET_NULL, null=True, blank=True)
    food_brand = models.ForeignKey('partnerships.Partner', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'partner_type': 'food_brand'})
```

---

## 🔧 IMPLEMENTATION PRIORITY

### **Phase 1: Foundation (Critical)**
1. ✅ Migrate to PostgreSQL
2. ✅ Add Service Layer
3. ✅ Add Custom Managers/QuerySets
4. ✅ Add REST API (DRF)
5. ✅ Add Celery + Redis
6. ✅ Add caching (Redis)
7. ✅ Add error tracking (Sentry)

### **Phase 2: Core Features**
1. ✅ NFC Tag Reading
2. ✅ Medical Reports
3. ✅ Vaccine Reminders (background tasks)
4. ✅ Basic Route Management

### **Phase 3: Advanced Features**
1. ✅ Route Optimization
2. ✅ Partner Integrations (Vets)
3. ✅ Food Brand Partnerships
4. ✅ Advanced Notifications (SMS, Push)

### **Phase 4: Scale & Optimize**
1. ✅ Database indexing
2. ✅ Query optimization
3. ✅ CDN for media
4. ✅ API rate limiting
5. ✅ Monitoring & Analytics

---

## 📊 DATABASE MIGRATION PLAN

### **SQLite → PostgreSQL**

1. **Export data**:
```bash
python manage.py dumpdata > backup.json
```

2. **Update settings.py**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pawcentral',
        'USER': 'pawcentral_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

3. **Install dependencies**:
```bash
pip install psycopg2-binary
```

4. **Migrate**:
```bash
python manage.py migrate
python manage.py loaddata backup.json
```

---

## 🎯 NEXT STEPS

1. **Create service layer structure**
2. **Set up PostgreSQL**
3. **Add Celery + Redis**
4. **Refactor one view to use service layer (proof of concept)**
5. **Add REST API for one feature**
6. **Implement NFC reading**
7. **Add medical/vaccine models**
8. **Set up background tasks**

---

**Estimated Timeline**:
- Phase 1 (Foundation): 2-3 weeks
- Phase 2 (Core Features): 3-4 weeks
- Phase 3 (Advanced): 4-6 weeks
- Phase 4 (Scale): Ongoing

---

*This document should be updated as the architecture evolves.*

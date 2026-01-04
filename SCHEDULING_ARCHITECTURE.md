================================================================================
                    SERVICE SCHEDULING ARCHITECTURE
                              2026-01-04
================================================================================

📍 LOCATION OF SCHEDULE DATA
================================================================================

✅ ServiceSlot Model: reservations.models.ServiceSlot
   Location: /home/joao/pet_app/reservations/models.py
   Database: SQLite (db.sqlite3)
   
   Fields:
   - business (ForeignKey) → Business [NOW BUSINESS-SCOPED]
   - service (ForeignKey) → Service (grooming, training, walk, daycare, etc.)
   - date (DateField) → Day the slot is available
   - start_time (TimeField) → When it starts (e.g., 08:00)
   - end_time (TimeField) → When it ends (e.g., 12:00)
   - max_capacity (IntegerField) → How many pets can book (e.g., 5 for daycare)
   - booked_count (IntegerField) → Current bookings
   - is_available (BooleanField) → Can be disabled by staff
   
   Table: reservations_serviceslot


✅ BusinessUnavailableDay Model: reservations.models.BusinessUnavailableDay
   Location: /home/joao/pet_app/reservations/models.py
   Purpose: Mark when a business is closed/unavailable
   
   Fields:
   - business (ForeignKey) → Business
   - date (DateField) → The unavailable day
   - type (CharField) → closed | half_day | holiday | strike | special
   - reason (CharField) → e.g., "Christmas", "Staff training"
   - notes (TextField) → Additional info
   
   Table: reservations_businessunavailableday


🏢 BUSINESS SCOPING
================================================================================

✅ Each business manages its own schedule
   - ServiceSlots now have business field
   - Tutors see only their business's slots
   - Staff creates slots for their business only

Query Example:
   ServiceSlot.objects.filter(
       business=tutor.business,
       date__gte=today,
       is_available=True
   )


🔧 AUTO-SLOT GENERATION
================================================================================

✅ Function: ensure_service_slots_exist(business=None)
   Location: /home/joao/pet_app/reservations/utils.py
   
   Called automatically when:
   - Tutor loads dashboard
   - View: /tutor/dashboard/
   
   Creates:
   - 30 days worth of slots
   - All service types (daycare, grooming, training, walk)
   - Per business
   - Only if missing (no duplicates)
   
   Time Slots Created:
   - Daycare: 2 slots/day (8am-12pm, 2pm-6pm) × 5 spots = 10 spots/day
   - Grooming: 4 slots/day (9-11, 11-1, 2-4, 4-6) × 1 spot = 4 spots/day
   - Training: 3 slots/day (10-11, 2-3, 3-4) × 2 spots = 6 spots/day
   - Walk: 4 slots/day (8-9, 10-11, 2-3, 4-5) × 3 spots = 12 spots/day


🗓️ STAFF CALENDAR MANAGEMENT (TODO)
================================================================================

📋 Managers can:
   [ ] View all service slots in calendar format
   [ ] Create/edit service slots
   [ ] Delete service slots
   [ ] Mark days as unavailable (holidays, strikes, closures)
   [ ] Set half-day operations
   [ ] See booking requests

Location: Staff Dashboard → Calendar Management Tab
URL: /staff/calendar/ (needs to be created)


🐕 TUTOR BOOKING FLOW
================================================================================

Current:
   1. Select pet
   2. Select service type
   3. Calendar shows available dates
   4. Click date → select time slot
   5. Confirm booking

TODO - Multi-day Daycare Booking:
   1. Select pet
   2. Select "Daycare" service
   3. Calendar shows available dates
   4. Click "Start Date"
   5. Click "End Date" (date range selected)
   6. Confirm multi-day booking
   
   Should Create Multiple ServiceBooking Records:
   - One per day
   - Same pet
   - Can be managed as a group


📊 ADMIN PANEL ACCESS
================================================================================

Location: /admin/reservations/

Can manage:
- ServiceSlot (with business filter)
- BusinessUnavailableDay
- ServiceBooking
- Service types


🗄️ DATABASE TABLES
================================================================================

reservations_serviceslot
   - Stores all available service slots
   - Now business-scoped
   - Unique: (business, service, date, start_time)

reservations_businessunavailableday
   - Stores holidays, closures, half-days
   - Unique: (business, date)

reservations_servicebooking
   - Booking requests from tutors
   - References: ServiceSlot, Pet, Tutor


🔄 AUTOMATIC MAINTENANCE
================================================================================

✅ Slots created on-demand:
   - First dashboard load
   - Always maintains 30-day window
   - No manual commands needed

⚠️ Old slots:
   - Not auto-deleted
   - Can be cleaned up via management command
   - Or manually in admin

[ ] TODO: Add scheduled task to clean old slots
   - Could use Celery Beat
   - Or APScheduler
   - Or simple Django command with cron


📱 TUTOR INTERFACE
================================================================================

Location: /tutor/dashboard/
Tab: Schedule → Book Services

Workflow:
1. Step 1: Choose Pet (dropdown)
   - Disable service/calendar until pet selected

2. Step 2: Choose Service (radio buttons)
   - Services loaded based on slots available for that pet
   - Disable calendar until service selected

3. Step 3: Pick Date (calendar)
   - Only show dates with slots for selected service
   - Highlight available dates
   - Disable unavailable dates (marked by business)

4. Click Date → Modal:
   - Show time slots for that date/service
   - For daycare: allow multiple selections (morning + afternoon)
   - For others: single selection
   - Add booking notes (optional)
   - Confirm → pending approval from staff


🚀 FUTURE ENHANCEMENTS
================================================================================

High Priority:
1. Multi-day daycare booking (date range)
2. Staff calendar management UI
3. Bulk slot creation by staff

Medium Priority:
4. Dynamic slot pricing
5. Recurring bookings (weekly, monthly)
6. Cancellation/rescheduling
7. Slot templates (copy Mondays to all weeks)

Low Priority:
8. Payment integration
9. Email notifications
10. SMS reminders


🔐 BUSINESS ISOLATION
================================================================================

✅ Tutors see only their business's slots
✅ Staff sees only their business's slots
✅ Slots are business-scoped in queries
✅ Unavailable days are business-specific

Enforcement:
- tutor.business → filter by business
- staff.business → filter by business
- Middleware checks access


📞 SUPPORT NOTES
================================================================================

If slots not showing:
1. Check tutors's business is set correctly
2. Check if date is within next 30 days
3. Check if slots exist: Admin → Reservations → Service Slots
4. Check if business is marked unavailable for that date

To manually create slots:
   python manage.py create_service_slots

To debug:
   from reservations.utils import ensure_service_slots_exist
   ensure_service_slots_exist()  # All businesses
   ensure_service_slots_exist(business=my_business)  # Single business


================================================================================
Last Updated: 2026-01-04
Author: Development Team
Status: Core architecture complete, UI pending
================================================================================

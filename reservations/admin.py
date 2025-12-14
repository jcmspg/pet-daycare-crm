from django.contrib import admin
from .models import CheckIn, PetAttendance, PetReservation, TutorSchedule, Service, ServiceSlot, ServiceBooking

@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('pet', 'is_present', 'checkin_time', 'checkout_time')
    list_filter = ('is_present',)

@admin.register(PetAttendance)
class PetAttendanceAdmin(admin.ModelAdmin):
    list_display = ('pet', 'date', 'checkin_time', 'checkout_time')
    list_filter = ('pet', 'date')
    search_fields = ('pet__name',)

@admin.register(PetReservation)
class PetReservationAdmin(admin.ModelAdmin):
    list_display = ('pet', 'type', 'date', 'time')
    list_filter = ('type', 'date', 'pet')
    search_fields = ('pet__name',)

@admin.register(TutorSchedule)
class TutorScheduleAdmin(admin.ModelAdmin):
    list_display = ('pet', 'tutor', 'type', 'date', 'start_time', 'end_time')
    list_filter = ('type', 'date', 'pet', 'tutor')
    search_fields = ('pet__name', 'tutor__name')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('type', 'duration_minutes', 'price')
    list_filter = ('type',)

@admin.register(ServiceSlot)
class ServiceSlotAdmin(admin.ModelAdmin):
    list_display = ('service', 'date', 'start_time', 'end_time', 'booked_count', 'max_capacity', 'is_available')
    list_filter = ('service', 'date', 'is_available')
    search_fields = ('service__type',)
    readonly_fields = ('booked_count',)

@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = ('pet', 'tutor', 'slot', 'status', 'requested_at')
    list_filter = ('status', 'slot__service', 'slot__date')
    search_fields = ('pet__name', 'tutor__name')
    readonly_fields = ('requested_at', 'confirmed_at', 'cancelled_at')

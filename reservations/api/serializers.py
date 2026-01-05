"""
API Serializers for Reservations app
"""
from rest_framework import serializers
from reservations.models import ServiceBooking, ServiceSlot, Service
from pets.models import Pet, Tutor


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for Service model"""
    class Meta:
        model = Service
        fields = ['id', 'type', 'duration_minutes', 'price', 'description']


class ServiceSlotSerializer(serializers.ModelSerializer):
    """Serializer for ServiceSlot model"""
    service = ServiceSerializer(read_only=True)
    available_spots = serializers.SerializerMethodField()
    is_fully_booked = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceSlot
        fields = [
            'id', 'service', 'date', 'start_time', 'end_time',
            'max_capacity', 'booked_count', 'is_available',
            'available_spots', 'is_fully_booked'
        ]
    
    def get_available_spots(self, obj):
        return obj.available_spots()
    
    def get_is_fully_booked(self, obj):
        return obj.is_fully_booked()


class PetSerializer(serializers.ModelSerializer):
    """Simplified Pet serializer for bookings"""
    class Meta:
        model = Pet
        fields = ['id', 'name', 'photo']


class TutorSerializer(serializers.ModelSerializer):
    """Simplified Tutor serializer for bookings"""
    class Meta:
        model = Tutor
        fields = ['id', 'name', 'email', 'phone']


class ServiceBookingSerializer(serializers.ModelSerializer):
    """Serializer for ServiceBooking model"""
    slot = ServiceSlotSerializer(read_only=True)
    pet = PetSerializer(read_only=True)
    tutor = TutorSerializer(read_only=True)
    slot_id = serializers.IntegerField(write_only=True, required=False)
    pet_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = ServiceBooking
        fields = [
            'id', 'slot', 'slot_id', 'pet', 'pet_id', 'tutor',
            'status', 'notes', 'requested_at', 'confirmed_at', 'cancelled_at'
        ]
        read_only_fields = ['id', 'status', 'requested_at', 'confirmed_at', 'cancelled_at']


class BookingConfirmSerializer(serializers.Serializer):
    """Serializer for booking confirmation"""
    booking_id = serializers.IntegerField(required=True)

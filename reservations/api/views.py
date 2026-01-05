"""
API Views for Reservations app
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from reservations.models import ServiceBooking, ServiceSlot
from reservations.services.booking_service import BookingService
from .serializers import ServiceBookingSerializer, ServiceSlotSerializer, BookingConfirmSerializer


class ServiceBookingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for ServiceBooking API endpoints.
    
    Provides read-only access to bookings with action endpoints for confirmation/cancellation.
    """
    serializer_class = ServiceBookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter bookings by user's business"""
        user = self.request.user
        
        # Staff users - all bookings for their business
        if hasattr(user, 'staff_profile') and user.staff_profile:
            business = user.staff_profile.business
            return ServiceBooking.objects.for_business(business).with_related()
        
        # Tutor users - only their bookings
        if hasattr(user, 'tutor_profile') and user.tutor_profile:
            tutor = user.tutor_profile
            return ServiceBooking.objects.for_tutor(tutor).with_related()
        
        return ServiceBooking.objects.none()
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Confirm a booking (staff only).
        
        POST /api/bookings/{id}/confirm/
        """
        booking = self.get_object()
        
        # Check if user is staff
        if not hasattr(request.user, 'staff_profile') or not request.user.staff_profile:
            return Response(
                {'error': 'Only staff members can confirm bookings'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            BookingService.confirm_booking(booking, request.user)
            return Response({
                'status': 'confirmed',
                'message': f'Booking confirmed for {booking.pet.name}'
            })
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a booking.
        
        POST /api/bookings/{id}/cancel/
        """
        booking = self.get_object()
        
        try:
            BookingService.cancel_booking(booking, reason=request.data.get('reason', ''))
            return Response({
                'status': 'cancelled',
                'message': f'Booking cancelled for {booking.pet.name}'
            })
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ServiceSlotViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for ServiceSlot API endpoints.
    
    Provides read-only access to available service slots.
    """
    serializer_class = ServiceSlotSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter slots by user's business"""
        user = self.request.user
        
        # Staff users - all slots for their business
        if hasattr(user, 'staff_profile') and user.staff_profile:
            business = user.staff_profile.business
            return ServiceSlot.objects.for_business(business).available().with_related()
        
        # Tutor users - slots for their business
        if hasattr(user, 'tutor_profile') and user.tutor_profile:
            business = user.tutor_profile.business
            return ServiceSlot.objects.for_business(business).available().with_related()
        
        return ServiceSlot.objects.none()
